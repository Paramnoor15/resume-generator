import React, { useState } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
  Paper,
  Grid,
} from "@mui/material";

function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [atsScore, setAtsScore] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleJobDescriptionChange = (e) => {
    setJobDescription(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); // Set loading state to true when submitting

    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);

    try {
      // Step 1: Upload the resume file
      const uploadResponse = await axios.post(
        "http://127.0.0.1:8000/upload_resume/", // Backend file upload endpoint
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      // File uploaded successfully
      setFileUploaded(true);

      console.log(uploadResponse.data);

      // Step 2: Parse the resume automatically after upload
      const analysisResponse = await axios.post(
        "http://127.0.0.1:8000/parse_resume/", // Endpoint for resume text extraction
        {
          file_name: uploadResponse.data.file_path.split("/").pop(), // Pass file name
        }
      );

      // Step 3: Fetch ATS score and suggestions
      setAtsScore(analysisResponse.data.ats_score);
      setSuggestions(analysisResponse.data.suggestions);
      setLoading(false); // Reset loading after analysis

    } catch (error) {
      console.error("Error uploading or analyzing resume:", error);
      setLoading(false); // Reset loading on error
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper sx={{ padding: 4, display: "flex", flexDirection: "column", gap: 2 }}>
        <Typography variant="h4" component="h1" textAlign="center">
          Resume Analyzer
        </Typography>
        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body1">Upload Resume (PDF):</Typography>
            <Button variant="contained" component="label">
              Choose File
              <input type="file" hidden onChange={handleFileChange} />
            </Button>
          </Box>

          <TextField
            label="Job Description"
            variant="outlined"
            fullWidth
            multiline
            rows={4}
            value={jobDescription}
            onChange={handleJobDescriptionChange}
            required
          />

          <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
            <Button variant="contained" type="submit" color="primary" disabled={loading}>
              {loading ? <CircularProgress size={24} /> : "Analyze Resume"}
            </Button>
          </Box>
        </form>

        {atsScore !== null && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" color="primary">
              ATS Analysis Result
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body1">ATS Score: {atsScore}</Typography>
            </Box>

            <Typography variant="body2" fontWeight="bold">Suggestions for Improvement:</Typography>
            <Grid container spacing={2}>
              {suggestions.map((suggestion, index) => (
                <Grid item xs={12} key={index}>
                  <Typography variant="body2">{suggestion}</Typography>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Paper>
    </Container>
  );
}

export default App;
