import streamlit as st
import os
import re
from candidate_profile import ProfileAI

# App Styling & Config
st.set_page_config(page_title="NaviGATHER AI for Resume parser, tip to improve resume and Cover Letter Generator", page_icon="🦾", layout="centered")

# Custom CSS for UI Styling
st.markdown(
    """
    <style>
        .main { background-color: #f9f9f9; }
        .stTextArea textarea { font-size: 14px; }
        .stButton button { font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white; border-radius: 8px; }
        .stButton button:hover { background-color: #45a049; }
        .stTextInput input { font-size: 14px; }
        .footer { font-size: 14px; text-align: center; padding-top: 20px; }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables for results
if "matching_score_response" not in st.session_state:
    st.session_state["matching_score_response"] = None

if "cover_letter" not in st.session_state:
    st.session_state["cover_letter"] = None

if "matching_score" not in st.session_state:
    st.session_state["matching_score"] = None
    
# Add a Logo (Make sure "logo.png" is in the same directory)
#st.image("app_images/logo.png")

# Title and Description
st.markdown("<h1 style='text-align: center;'>📄 NaviGATHER AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Upload your resume and job description, and let AI evaluate your matching score, give you advices to improve your resume and craft a professional cover letter.</p>", unsafe_allow_html=True)

# API Key Input
st.subheader("🔑 Insert Your API Key")
st.markdown(
    "🔑 **You can generate your API key here.** "
    "[here](https://www.llama-api.com/) 🔗",
    unsafe_allow_html=True
)

api_key = st.text_input("Enter your API key", type="password")

# File Upload
st.subheader("📂 Let me know you!")
st.write("Upload a **.docx** or **.pdf** file containing your resume. The AI will profile it for you.")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

if uploaded_file is not None and api_key:
    # Save uploaded file temporarily
    temp_file_path = f"temp_{uploaded_file.name}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(uploaded_file.read())

    # Process file with CoverLetterAI
    navigather_ai = ProfileAI(llm_api_key=api_key)  # Pass API key to backend
    navigather_ai.read_candidate_data(temp_file_path)

    # Remove temp file after processing (optional)
    os.remove(temp_file_path)

    # Display Extracted Resume Information
    st.subheader("🔍 AI is extracting your resume information")
    st.text_area("This is your profile overview", navigather_ai.profile_candidate(), height=300)

    # Job Description Input
    st.subheader("📌 Now tell me about your dream job")
    job_description = st.text_area("Copy paste the job description of the job that you like", "", height=200)

    
    if (job_description):
        navigather_ai.add_job_description(job_description)
        navigather_ai.read_jobdescription_data(job_description)
        # Display Extracted Resume Information
        st.subheader("🔍 AI is extracting your job description information")
        st.text_area("This job description overview", navigather_ai.profile_jobdesc(), height=300)

        # Generate Cover Letter
        if st.button("🔍 Check matching score"):
            matching_score_response = navigather_ai.write_matching_score()
            # Regex to find first number followed by %
            match = re.search(r'(\d+(?:\.\d+)?)%', matching_score_response)

            if match:
                matching_score = match.group(1)
                fig = navigather_ai.matching_score_visualization(float(matching_score))
                st.session_state["matching_score"] = fig
            # Store results in session state
            st.session_state["matching_score_response"] = matching_score_response
        
        # Generate Cover Letter
        if st.button("✍️ Generate Cover Letter"):

            cover_letter = navigather_ai.write_cover_letter()
            # Store cover letter in session state
            st.session_state["cover_letter"] = cover_letter

    else:
        st.warning("⚠️ Please enter your dream job.")
elif uploaded_file is not None and not api_key:
    st.warning("⚠️ Please enter your API key before proceeding.")

# Display results (persisted in session state)
if st.session_state["matching_score_response"]:
    st.subheader("🪄 Matching Score")
    if st.session_state["matching_score"]:
        st.plotly_chart(st.session_state["matching_score"], use_container_width=True)
    st.markdown(st.session_state["matching_score_response"])

if st.session_state["cover_letter"]:
    st.subheader("🪄 Enjoy the magic")
    st.text_area("This is the AI-generated cover letter!", st.session_state["cover_letter"], height=300)

# Footer with Credits
st.markdown(
    """
    <div class="footer">
        <p>Edited based on version of CoverLetterAI from <b>Piero Paialunga</b> at https://github.com/PieroPaialungaAI/CoverLetterAI/tree/main</p>
    </div>
    """,
    unsafe_allow_html=True
)
