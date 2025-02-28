import streamlit as st
import PyPDF2
import google.generativeai as genai 

# Set your Gemini API Key
GEMINI_API_KEY = 'AIzaSyDT5161mUjmkK8ywECD26_ZR3YaSjC-X4U'  
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
    
    
    model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-1219') 
    
    try:
        response = model.generate_content(prompt)
        result = response.text
        
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

def process_resume(uploaded_file, job_description):
    """Processes an uploaded resume file and returns its score, analysis, and key skills."""
    if uploaded_file is not None:
        resume_text = extract_text_from_pdf(uploaded_file)
        score, analysis, key_skills = get_resume_score(resume_text, job_description)
        st.session_state.resume_history.append({
            "job_description": job_description, 
            "resume_file_name": uploaded_file.name,  
            "resume_text": resume_text,
            "score": score,
            "analysis": analysis,
            "key_skills": key_skills
        })
        return score, analysis, key_skills
    return None, None, None

def rank_resumes():
    """Ranks resumes based on their score."""
    return sorted(st.session_state.resume_history, key=lambda x: x["score"], reverse=True)


st.title("AI-Powered Resume Screening & Ranking")

job_description = st.text_area("Enter Job Description:")

uploaded_file = st.file_uploader("Upload Resume (PDF format only)", type=["pdf"])

if st.button("Analyze Resume"):
    if uploaded_file and job_description:
        score, analysis, key_skills = process_resume(uploaded_file, job_description)
        if score is not None:
            st.success(f"Resume Score: {score}/100")
            st.write(f"Analysis: {analysis}")
            st.write(f"Key Skills: {key_skills}")
        else:
            st.error("Failed to process the resume.")
    else:
        st.error("Please upload a resume and enter a job description.")

st.subheader("Ranked Resumes")
if st.session_state.resume_history:
    ranked_resumes = rank_resumes()
    for i, resume_data in enumerate(ranked_resumes, start=1):
        st.write(f"{i}. Score: {resume_data['score']}")
        st.write(f"Job Description: {resume_data['job_description']}")
        st.write(f"Resume File Name: {resume_data['resume_file_name']}")
        st.write(f"Analysis: {resume_data['analysis']}")
        st.write(f"Key Skills: {resume_data['key_skills']}")
        st.write("---") 
else:
    st.write("No resumes analyzed yet.")