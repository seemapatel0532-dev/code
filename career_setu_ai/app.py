
import streamlit as st
import PyPDF2
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="CareerSetu AI", layout="wide")

st.title("🚀 CareerSetu - Smart Resume Analyzer")

# Upload Resume
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

# Job Description
job_desc = st.text_area("Enter Job Description")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)
    return text

def calculate_similarity(resume, jd):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume, jd])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(similarity * 100, 2)

if st.button("Analyze Resume"):
    if uploaded_file is None or job_desc.strip() == "":
        st.warning("Please upload resume and enter job description")
    else:
        resume_text = extract_text_from_pdf(uploaded_file)
        resume_clean = clean_text(resume_text)
        jd_clean = clean_text(job_desc)

        score = calculate_similarity(resume_clean, jd_clean)

        st.success(f"Match Score: {score}%")

        if score > 75:
            st.info("Excellent match! 🎯")
        elif score > 50:
            st.info("Good match 👍")
        else:
            st.info("Needs improvement ⚠️")
