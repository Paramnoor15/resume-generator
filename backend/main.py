import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, HTTPException, File, UploadFile
import shutil
import os
import datetime
import fitz     
import re
import logging
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Firebase Admin SDK with your credentials file
cred = credentials.Certificate("resume-generator-5673d-firebase-adminsdk-fbsvc-77d42958de.json")
firebase_admin.initialize_app(cred)

# Access Firestore
db = firestore.client()

# Create FastAPI app
app = FastAPI()

# Directory to store uploaded PDFs
UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create folder if it doesn't exist

# Create a model for the request body
class ResumeRequest(BaseModel):
    file_name: str

# Root route (optional)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume & Cover Letter Generator!"}

# 📌 Save Resume Endpoint
@app.post("/save_resume/")
async def save_resume(data: dict):
    try:
        # Save resume data to Firestore
        result = db.collection("resumes").add({
            "name": data.get("name"),
            "job_description": data.get("job_description"),
            "resume_text": data.get("resume_text"),
        })
        
        # Unpack the result correctly
        _, resume_ref = result  # Get document reference

        # Return the document ID
        return {"message": "Resume saved successfully", "id": resume_ref.id}
    
    except Exception as e:
        logging.error(f"Error saving resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving resume: {str(e)}")

# 📌 Get Resumes Endpoint
@app.get("/get_resumes/")
async def get_resumes():
    try:
        # Fetch all documents from the "resumes" collection
        resumes = db.collection("resumes").stream()

        # Create a list of resumes to return as JSON
        resume_list = []
        for resume in resumes:
            resume_dict = resume.to_dict()  # Convert document data to dictionary
            resume_dict["id"] = resume.id  # Add document ID to the data
            resume_list.append(resume_dict)

        # Return the list of resumes
        return {"resumes": resume_list}

    except Exception as e:
        logging.error(f"Error retrieving resumes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving resumes: {str(e)}")

# 📌 PDF Upload Endpoint
@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to the uploads folder
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Store metadata in Firestore
        file_metadata = {
            "file_name": file.filename,
            "file_path": file_path,
            "file_size": file.file.tell(),  # Get file size in bytes
            "upload_time": datetime.datetime.utcnow().isoformat()
        }
        db.collection("uploaded_resumes").add(file_metadata)

        return {"message": f"File '{file.filename}' uploaded successfully!", "file_path": file_path}
    
    except Exception as e:
        logging.error(f"Error uploading resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading resume: {str(e)}")

# 📌 Resume Parsing Endpoint
@app.post("/parse_resume/")
async def parse_resume(request: ResumeRequest):
    """Extract text from an uploaded PDF and save it to Firestore."""
    try:
        file_name = request.file_name
        file_path = os.path.join(UPLOAD_DIR, file_name)

        # Ensure the file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found.")

        # Extract text from the PDF
        resume_text = extract_text_from_pdf(file_path)

        # Save extracted text in Firestore
        parsed_data = {
            "file_name": file_name,
            "resume_text": resume_text
        }
        db.collection("parsed_resumes").add(parsed_data)

        return {"message": f"Resume text extracted and saved successfully!", "resume_text": resume_text}

    except Exception as e:
        logging.error(f"Error parsing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


# Function to extract text from a PDF file
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF and clean the extracted text."""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text("text")  # Extract text from each page

        # Basic cleanup: Remove extra spaces, page numbers, and other unwanted content
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        return cleaned_text
    
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")
