import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI

# Initialize Firebase Admin SDK with your credentials file
cred = credentials.Certificate("resume-generator-5673d-firebase-adminsdk-fbsvc-77d42958de.json")
firebase_admin.initialize_app(cred)

# Access Firestore
db = firestore.client()

app = FastAPI()

# Root route (optional)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume & Cover Letter Generator!"}

# Save Resume endpoint
@app.post("/save_resume/")
async def save_resume(data: dict):
    try:
        # Save resume data to Firestore
        result = db.collection("resumes").add({
            "name": data.get("name"),
            "job_description": data.get("job_description"),
            "resume_text": data.get("resume_text"),
        })
        
        # Log both parts of the response for debugging
        print(f"Firestore Result (Full): {result}")
        print(f"Firestore Result - First Element (Timestamp): {result[0]}")
        print(f"Firestore Result - Second Element (DocumentReference): {result[1]}")
        
        # Unpack the result correctly
        _, resume_ref = result  # Swap the unpacking order

        # Return the document ID
        return {"message": "Resume saved successfully", "id": resume_ref.id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving resume: {str(e)}")

# Get Resumes endpoint
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
        raise HTTPException(status_code=500, detail=f"Error retrieving resumes: {str(e)}")
