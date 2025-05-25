import streamlit as st
import sys
import os
import time
import io
from pypdf import PdfReader
import logging
from utils import job_details_llm_response, extract_skills_from_job_description

# Suppress specific PyTorch-related warnings
logging.getLogger('streamlit.watcher.local_sources_watcher').setLevel(logging.ERROR)

# Set page configuration
st.set_page_config(
    page_title="JobSphere: AI-Powered Job Search",
    page_icon="💼",
    layout="wide"
)

# Simple, clean CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    
    .job-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .score-badge {
        background: #48bb78;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
    }
    
    .stButton > button {
        width: 100%;
        background: #667eea;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    
    .stButton > button:hover {
        background: #5a6fd8;
    }
    </style>
""", unsafe_allow_html=True)

# Safely import graph module  
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from graph import create_graph
    compiled_graph = create_graph()
    graph_loaded = True
except Exception as e:
    st.info("Running in demo mode")
    compiled_graph = None
    graph_loaded = False

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "home"
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {}
if "ranked_jobs" not in st.session_state:
    st.session_state.ranked_jobs = []
if "jobs_loaded" not in st.session_state:
    st.session_state.jobs_loaded = False
if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = None
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "list"
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

# Function to reset session state
def reset_session():
    for key in list(st.session_state.keys()):
        if key != "page":
            del st.session_state[key]
    st.session_state.page = "home"
    st.rerun()

# Function to go back to home
def go_back_home():
    st.session_state.page = "home"
    st.rerun()

# Function to view job details
def view_job_details(job_index):
    st.session_state.selected_job_id = job_index
    st.session_state.view_mode = "detail"
    st.rerun()

# Function to return to job list
def back_to_list():
    st.session_state.view_mode = "list"
    st.rerun()

# Home page
def home_page():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>JobSphere 💼</h1>
            <p>Your AI-Powered Job Search Assistant</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Choose Your Path")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("#### 🎯 Customize Your Search")
        st.write("Set detailed preferences for personalized job recommendations")
        if st.button("Start with Preferences", key="pref_btn"):
            st.session_state.page = "preferences"
            st.rerun()
    
    with col2:
        st.markdown("#### 📄 Quick AI Analysis")
        st.write("Upload your resume for automatic skill extraction")
        if st.button("Upload Resume", key="resume_btn"):
            st.session_state.page = "resume"
            st.rerun()

# Preferences form page
def preferences_page():
    if st.button("← Back to Home"):
        go_back_home()
    
    st.title("Your Job Preferences")
    st.write("Tell us what you're looking for and we'll find the perfect matches")
    
    with st.form(key='preferences_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            role = st.text_input("Desired Role *", placeholder="e.g., Software Engineer")
            location = st.text_input("Preferred Location *", placeholder="e.g., Bangalore, India")
            experience = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
        
        with col2:
            salary = st.number_input("Minimum Salary (INR)", min_value=0, step=100000)
            company_size_options = ["Startup", "Small/Medium Enterprise", "MNC", "Any"]
            company_size = st.selectbox("Preferred Company Size", company_size_options)
        
        skills = st.text_area("Skills *", placeholder="e.g., Python, SQL, Project Management")
        company_description = st.text_area("Desired Company Culture (Optional)", 
                                         placeholder="e.g., innovative, remote-friendly, diverse")
        
        submit_button = st.form_submit_button(label="🚀 Find My Perfect Job")
        
        if submit_button:
            if role and location and skills:
                st.session_state.user_preferences = {
                    "role": role,
                    "experience": experience,
                    "skills": skills,
                    "salary": salary,
                    "location": location,
                    "company_size": company_size,
                    "company_description": company_description
                }
                st.session_state.form_submitted = True
                st.session_state.jobs_loaded = False
                st.session_state.view_mode = "list"
                st.session_state.page = "jobs"
                st.rerun()
            else:
                st.error("Please fill in the required fields (*)")

# Resume upload page
def resume_upload_page():
    if st.button("← Back to Home"):
        go_back_home()
    
    st.title("Quick Setup with Resume")
    st.write("Upload your resume and let our AI do the heavy lifting")
    
    # Resume upload section
    st.subheader("📄 Upload Your Resume")
    resume = st.file_uploader("Choose your resume file", type=["pdf"])
    
    if resume:
        st.success(f"✅ Resume uploaded: {resume.name}")
        st.info("🤖 Our AI will extract your skills and experience automatically!")
    
    st.subheader("🎯 Basic Preferences")
    
    with st.form(key='resume_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            role = st.text_input("Desired Role *", placeholder="e.g., Software Engineer")
            location = st.text_input("Preferred Location *", placeholder="e.g., Bangalore, India")
        
        with col2:
            experience = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
            salary = st.number_input("Minimum Salary (INR)", min_value=0, step=100000)
        
        submit_button = st.form_submit_button(label="🚀 Analyze Resume & Find Jobs")
        
        if submit_button:
            if role and location:
                if resume:
                    reader = PdfReader(resume)
                    resume_text = ""
                    for page in reader.pages:
                        resume_text += page.extract_text()
                    print("Resume as text: \n" + resume_text)
                    extracted_skills = extract_skills_from_job_description(resume_text)
                    extracted_skills = ', '.join(extracted_skills)
                else:
                    extracted_skills = ""
                    st.warning("⚠️ No resume uploaded. Please add your skills manually in the next step.")
                
                st.session_state.user_preferences = {
                    "role": role,
                    "experience": experience,
                    "skills": extracted_skills,
                    "salary": salary,
                    "location": location,
                    "company_size": "Any",
                    "company_description": ""
                }
                st.session_state.form_submitted = True
                st.session_state.jobs_loaded = False
                st.session_state.view_mode = "list"
                st.session_state.page = "jobs"
                st.rerun()
            else:
                st.error("Please fill in the required fields (*)")

# Jobs page
def jobs_page():
    if not st.session_state.jobs_loaded:
        # Show progress while fetching jobs
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_steps = [
            "🔍 Analyzing your preferences...",
            "🌐 Searching job databases...",
            "🎯 Matching skills with opportunities...",
            "📊 Calculating relevance scores...",
            "🏆 Ranking positions just for you..."
        ]
        
        for i, step in enumerate(status_steps):
            progress_value = (i + 1) / len(status_steps)
            progress_bar.progress(progress_value)
            status_text.write(step)
            time.sleep(1)
            
        # Generate jobs data
        try:
            if graph_loaded and compiled_graph is not None:
                final_state = compiled_graph.invoke({"user_preferences": st.session_state.user_preferences})
                if "ranked_jobs" in final_state:
                    st.session_state.ranked_jobs = final_state["ranked_jobs"]
                else:
                    st.session_state.ranked_jobs = []
            else:
                # Demo mode - use mock data
                st.session_state.ranked_jobs = [
                    {
                        "job_details": {
                            "job_title": "Senior Software Engineer",
                            "employer_name": "TechCorp Inc.",
                            "job_description": "We are looking for an experienced Software Engineer to join our team. You will be responsible for developing high-quality applications and services using modern technologies.",
                            "job_city": "Bangalore",
                            "job_country": "India",
                            "job_employment_type": "Full-time",
                            "job_salary_range": "24-30 LPA",
                            "job_apply_link": "https://example.com/apply"
                        },
                        "relevance_score": 0.85
                    },
                    {
                        "job_details": {
                            "job_title": "ML Engineer",
                            "employer_name": "AI Innovations",
                            "job_description": "We're seeking an ML Engineer to develop and deploy machine learning models in production environments. Experience with Python, TensorFlow, and cloud platforms required.",
                            "job_city": "Bangalore",
                            "job_country": "India",
                            "job_employment_type": "Hybrid",
                            "job_salary_range": "22-32 LPA",
                            "job_apply_link": "https://example.com/apply2"
                        },
                        "relevance_score": 0.75
                    },
                    {
                        "job_details": {
                            "job_title": "Data Scientist",
                            "employer_name": "DataTech Solutions",
                            "job_description": "Join our data science team to build predictive models and extract insights from large datasets. Strong background in statistics and machine learning required.",
                            "job_city": "Mumbai",
                            "job_country": "India",
                            "job_employment_type": "Full-time",
                            "job_salary_range": "20-28 LPA",
                            "job_apply_link": "https://example.com/apply3"
                        },
                        "relevance_score": 0.65
                    }
                ]
            
            st.session_state.jobs_loaded = True
            
        except Exception as e:
            st.error(f"Error processing job data: {str(e)}")
            st.session_state.ranked_jobs = []
        
        progress_bar.empty()
        status_text.empty()
        st.rerun()
    
    # Display jobs
    if st.session_state.jobs_loaded:
        if len(st.session_state.ranked_jobs) > 0:
            st.success(f"🎉 Found {len(st.session_state.ranked_jobs)} matching jobs for you")
            
            # DETAIL VIEW
            if st.session_state.view_mode == "detail" and st.session_state.selected_job_id is not None:
                if st.button("← Back to Job List"):
                    back_to_list()
                
                job_index = st.session_state.selected_job_id
                
                if 0 <= job_index < len(st.session_state.ranked_jobs):
                    current_job = st.session_state.ranked_jobs[job_index]
                    job_details = current_job.get("job_details", {})
                    relevance_score = current_job.get("relevance_score", 0)
                    
                    # Job header
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.title(job_details.get('job_title', 'Job Title'))
                        st.subheader(job_details.get('employer_name', 'Company'))
                        job_location = f"{job_details.get('job_location')}"
                        st.write(f"📍 {job_location}")
                    
                    with col2:
                        st.markdown(f"""
                            <div class="score-badge">
                                Match Score<br>
                                <span style='font-size: 24px;'>{int(relevance_score * 100)}%</span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Job description
                    st.subheader("Job Description")
                    st.write(job_details.get('job_description', 'No description available.'))
                    
                    # Apply button
                    job_apply_link = job_details.get('job_apply_link', '#')
                    st.markdown(f'<a href="{job_apply_link}" target="_blank"><button style="background:#667eea;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">Apply Now 🚀</button></a>', unsafe_allow_html=True)
                    
                    # Navigation
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        if job_index > 0:
                            if st.button("← Previous Job"):
                                view_job_details(job_index - 1)
                    with col3:
                        if job_index < len(st.session_state.ranked_jobs) - 1:
                            if st.button("Next Job →"):
                                view_job_details(job_index + 1)
                    
                    st.info(f"📋 Viewing job {job_index + 1} of {len(st.session_state.ranked_jobs)}")
                    
                    # Chatbot section
                    st.markdown("---")
                    st.subheader("💬 Chat with JobSphere AI")
                    st.write(f"Ask questions about the {job_details.get('job_title')} role at {job_details.get('employer_name')}.")
                    
                    if job_index not in st.session_state.chat_histories:
                        st.session_state.chat_histories[job_index] = []
                    chat_history = st.session_state.chat_histories[job_index]
                    
                    for message in chat_history:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                    
                    user_input = st.chat_input("Type your message here...")
                    if user_input:
                        chat_history.append({"role": "user", "content": user_input})
                        with st.chat_message("user"):
                            st.markdown(user_input)
                        with st.spinner("JobSphere AI is generating a response..."):
                            job_description = job_details.get("job_description", "")
                            ai_response = job_details_llm_response(user_input, job_description)
                        chat_history.append({"role": "assistant", "content": ai_response})
                        with st.chat_message("assistant"):
                            st.markdown(ai_response)
                else:
                    st.error("Invalid job selection")
                    back_to_list()
            
            # LIST VIEW
            else:
                st.subheader("🎯 Recommended Jobs for You")
                
                for i, job in enumerate(st.session_state.ranked_jobs):
                    job_details = job.get("job_details", {})
                    relevance_score = job.get("relevance_score", 0)
                    
                    with st.container():                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{job_details.get('job_title', 'Job Title')}** | {job_details.get('employer_name', 'Company')}")
                            location_text = f"{job_details.get('job_location')}"
                            st.write(f"📍 {location_text}")
                            
                            if st.button(f"View Details", key=f"view_{i}"):
                                view_job_details(i)
                        
                        with col2:
                            st.markdown(f"""
                                <div class="score-badge">
                                    Match: {int(relevance_score * 100)}%
                                </div>
                            """, unsafe_allow_html=True)
                            
                            job_apply_link = job_details.get('job_apply_link', '#')
                            st.markdown(f'<a href="{job_apply_link}" target="_blank"><button style="background:#48bb78;color:white;padding:8px 16px;border:none;border-radius:5px;cursor:pointer;margin-top:10px;">Quick Apply</button></a>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown("---")
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Refine Search"):
                        st.session_state.page = "preferences"
                        st.rerun()
                with col2:
                    if st.button("🆕 Start New Search"):
                        reset_session()
        else:
            st.warning("🔍 No jobs found matching your preferences.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Modify Preferences"):
                    st.session_state.page = "preferences"
                    st.rerun()
            with col2:
                if st.button("🏠 Back to Home"):
                    reset_session()

# Main navigation logic
if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "preferences":
    preferences_page()
elif st.session_state.page == "resume":
    resume_upload_page()
elif st.session_state.page == "jobs":
    jobs_page()