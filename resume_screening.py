import streamlit as st
import PyPDF2
import google.generativeai as genai  # Import the Gemini library

# Set your Gemini API Key
GEMINI_API_KEY = 'AIzaSyDT5161mUjmkK8ywECD26_ZR3YaSjC-X4U'  # Replace with your actual Gemini API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize session state for resume history
if "resume_history" not in st.session_state:
    st.session_state.resume_history = []

def get_resume_score(resume_text, job_description):
    """Uses Gemini API to classify and score resume relevance based on the job description."""
    prompt = (f"""
    You are an AI that scores resumes based on their relevance to a job description.
    Given the following job description and resume, provide:
    1. A score from 0 to 100, where 100 means a perfect match.
    2. A brief analysis of the resume's strengths and weaknesses in relation to the job description.
    3. An ordered list of key skills present in the resume.
    
    Job Description:
    {job_description}
    
    Resume:
    {resume_text}
    
    Please provide the response in the following format:
    Score: [score]/100
    Analysis: [brief analysis]
    Key Skills: [comma-separated list of key skills]
    """
    )
    
    # Initialize the Gemini model
    model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-1219')  # Use the Gemini Pro model
    
    try:
        # Generate response using Gemini
        response = model.generate_content(prompt)
        result = response.text
        
        # Extract score, analysis, and key skills from the response
        score = int(result.split("Score: ")[1].split("/")[0])
        analysis = result.split("Analysis: ")[1].split("Key Skills: ")[0].strip()
        key_skills = result.split("Key Skills: ")[1].strip()
        return score, analysis, key_skills
    except Exception as e:
        print(f"Error: {e}")
        return 0, "Failed to process the request.", ""

def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file."""
    reader = PyPDF2.PdfReader(uploaded_file)
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def process_resumes(uploaded_files, job_description):
    """Processes multiple uploaded resume files and returns their scores, analyses, and key skills."""
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            resume_text = extract_text_from_pdf(uploaded_file)
            score, analysis, key_skills = get_resume_score(resume_text, job_description)
            st.session_state.resume_history.append({
                "job_description": job_description,  # Store the job description
                "resume_file_name": uploaded_file.name,  # Store the resume file name
                "resume_text": resume_text,
                "score": score,
                "analysis": analysis,
                "key_skills": key_skills
            })

def rank_resumes():
    """Ranks resumes based on their score."""
    return sorted(st.session_state.resume_history, key=lambda x: x["score"], reverse=True)

# Streamlit UI
st.title("AI-Powered Resume Screening & Ranking")

# User input for job description
job_description = st.text_area("Enter Job Description:")

# File upload for multiple resumes
uploaded_files = st.file_uploader("Upload Resumes (PDF format only, multiple allowed)", type=["pdf"], accept_multiple_files=True)

if st.button("Analyze Resumes"):
    if uploaded_files and job_description:
        process_resumes(uploaded_files, job_description)
        st.success("Resumes processed successfully!")
    else:
        st.error("Please upload at least one resume and enter a job description.")

# Display ranked resumes
st.subheader("Ranked Resumes")
if st.session_state.resume_history:
    ranked_resumes = rank_resumes()
    for i, resume_data in enumerate(ranked_resumes, start=1):
        st.write(f"{i}. Score: {resume_data['score']}")
        st.write(f"Job Description: {resume_data['job_description']}")
        st.write(f"Resume File Name: {resume_data['resume_file_name']}")
        st.write(f"Analysis: {resume_data['analysis']}")
        st.write(f"Key Skills: {resume_data['key_skills']}")
        st.write("---")  # Add a separator between resumes
else:
    st.write("No resumes analyzed yet.")
