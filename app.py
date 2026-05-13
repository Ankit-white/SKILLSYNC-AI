import streamlit as st
import pandas as pd
import numpy as np
import PyPDF2
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

import requests
# webpage configuration
st.set_page_config(
    page_title="InterviewIQ",
    layout="wide"
)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = None

#ui design
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
}
.big-title {
    font-size: 44px;
    font-weight: 800;
    color: #38bdf8;
}
.subtitle {
    font-size: 18px;
    color: #cbd5e1;
}
.card {
    background-color: #1e293b;
    padding: 22px;
    border-radius: 16px;
    margin: 12px 0;
    color: white;
}
</style>
""", unsafe_allow_html=True)
#display the things
st.markdown("<div class='big-title'>InterviewIQ</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI Interview & Skill Assessment Platform</div>", unsafe_allow_html=True)
st.write("")

skills_list = [
    "python", "java", "c++", "html", "css", "javascript",
    "react", "nodejs", "mongodb", "sql", "machine learning",
    "data science", "numpy", "pandas", "opencv", "firebase",
    "django", "flask"
]
#fileuploading using file_uploader
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    st.success("Resume Uploaded Successfully!")

    pdf_reader = PyPDF2.PdfReader(uploaded_file)

    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "

    text = text.lower()

    st.subheader("Extracted Resume Text")
    st.text_area("Resume Content", text, height=250)

    detected_skills = []

    for skill in skills_list:
        if skill in text:
            detected_skills.append(skill)

    missing_skills = list(set(skills_list) - set(detected_skills))
    #using of pandas for dataframe of skills
    skills_df = pd.DataFrame({
        "Detected Skills": pd.Series(detected_skills),
        "Missing Skills": pd.Series(missing_skills)
    })
# using numpy for ats calculation

    detected_array = np.array(detected_skills)

    ats_score = np.round(
        (detected_array.size / len(skills_list)) * 100
    ).astype(int)

    st.subheader("Detected Skills")
    st.write(detected_skills)

    st.subheader("Skills Data Table")
    st.dataframe(skills_df)

    st.subheader("ATS Score")
    st.progress(int(ats_score))
    st.write(f"ATS Score: {ats_score}%")

    st.subheader("Candidate Performance Level")

    if ats_score >= 80:
        st.success("Expert Level Candidate")
    elif ats_score >= 60:
        st.info("Advanced Level Candidate")
    elif ats_score >= 40:
        st.warning("Intermediate Level Candidate")
    else:
        st.error("Beginner Level Candidate")

    st.subheader("Missing Skills")
    st.write(missing_skills)

    st.subheader("Skills Analysis")

    labels = ["Detected Skills", "Missing Skills"]
    values = [len(detected_skills), len(missing_skills)]
    #shows graph

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_ylabel("Count")
    ax.set_title("Resume Skill Analysis")
    st.pyplot(fig)

    if st.button("Generate AI Interview Questions"):

        api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        st.error("OpenRouter API key missing.")

    else:

        prompt = f"""
        Generate 10 interview questions for a candidate.

        Skills:
        {detected_skills}

        Resume:
        {text[:2000]}

        Include beginner to advanced questions.
        """

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )

            result = response.json()

            ai_text = result['choices'][0]['message']['content']

            st.markdown(
                f"<div class='card'>{ai_text}</div>",
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"AI Error: {e}")

        else:
            st.info("Please upload a resume PDF to start analysis.")