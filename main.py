import streamlit as st
import sys
import os
import time
import logging
from utils import job_details_llm_response

logging.getLogger('streamlit.watcher.local_sources_watcher').setLevel(logging.ERROR)

st.set_page_config(
    page_title="JobSphere: AI-Powered Job Search",
    page_icon="💼",
    layout="wide"
)

st.markdown("""
    <style>
    .job-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 0;
    }
    .company-name {
        font-size: 18px;
        color: #4a4a4a;
        margin-top: 0;
    }
    .relevance-score {
        background-color: #f0f7ff;
        padding: 10px;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
    }
    .job-description {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
        max-height: 400px;
        overflow-y: auto;
    }
    .apply-button {
        text-align: center;
        margin-top: 20px;
    }
    .job-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
        transition: transform 0.3s, box-shadow 0.3s;
        cursor: pointer;
    }
    .job-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .job-card-title {
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 5px;
    }
    .job-card-company {
        font-size: 14px;
        color: #555;
        margin-bottom: 10px;
    }
    .job-card-details {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: #666;
    }
    .selected-job-card {
        border: 2px solid #4CAF50;
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.2);
    }
    .badge {
        background-color: #e7f3ff;
        color: #0366d6;
        border-radius: 12px;
        padding: 3px 8px;
        font-size: 12px;
        font-weight: 500;
    }
    .score-badge {
        background-color: #e7f8e7;
        color: #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# Page title
st.title("JobSphere: Your AI-Powered Job Search Assistant")

try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from graph import create_graph
    compiled_graph = create_graph()
    graph_loaded = True
except Exception as e:
    st.warning(f"Notice: Running in demo mode (graph module not loaded)")
    compiled_graph = None
    graph_loaded = False

# Initialize session state variables
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {}
if "current_job_index" not in st.session_state:
    st.session_state.current_job_index = 0
if "ranked_jobs" not in st.session_state:
    st.session_state.ranked_jobs = []
if "jobs_loaded" not in st.session_state:
    st.session_state.jobs_loaded = False
if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = None
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "list"  # Can be "list" or "detail"
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

# Function to reset session state
def reset_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
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

# User preferences form
if not st.session_state.form_submitted:
    with st.form(key='user_preferences_form'):
        st.subheader('Please provide your job preferences below')
        
        col1, col2 = st.columns(2)
        
        with col1:
            role = st.text_input("Desired Role", placeholder="eg. Software Engineer")
            experience = st.number_input("Experience (Years)", min_value=0, max_value=50, step=1)
            skills = st.text_area("Skills", placeholder="List your skills, separated by commas")
        
        with col2:
            salary = st.number_input("Minimum Salary Expectation (in INR)", min_value=0, step=100000)
            location = st.text_input("Location", placeholder="Preferred location for the job. Format = Location, Country")
            company_size_options = ["Startup", "Small/Medium Enterprise", "MNC", "Any"]
            company_size = st.selectbox("Preferred Company Size", company_size_options)
        
        company_description = st.text_area("Desired Company Attributes (Optional)",
                                           placeholder="e.g., innovative, remote-friendly")

        submit_button = st.form_submit_button(label="Find My Perfect Job")

        if submit_button:
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
            st.rerun()

# Display jobs if form is submitted
if st.session_state.form_submitted:
    if not st.session_state.jobs_loaded:
        # Show progress bar while fetching jobs
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_steps = [
            "Analyzing your preferences...",
            "Searching job databases...",
            "Matching skills with opportunities...",
            "Calculating relevance scores...",
            "Ranking positions just for you..."
        ]
        
        for i, step in enumerate(status_steps):
            progress_value = (i + 1) / len(status_steps)
            progress_bar.progress(progress_value)
            status_text.text(step)
            time.sleep(15)  # Simulate processing time
            
        # Generate mock data for testing or use the graph to get real data
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
                            "job_description": "We are looking for an experienced Software Engineer to join our team. You will be responsible for developing high-quality applications and services.",
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
                            "job_description": "We're seeking an ML Engineer to develop and deploy machine learning models in production environments.",
                            "job_city": "Bangalore",
                            "job_country": "India",
                            "job_employment_type": "Hybrid",
                            "job_salary_range": "22-32 LPA",
                            "job_apply_link": "https://example.com/apply5"
                        },
                        "relevance_score": 0.65
                    }
                ]
            
            st.session_state.jobs_loaded = True
            
        except Exception as e:
            st.error(f"Error processing job data: {str(e)}")
            st.session_state.ranked_jobs = []
        
        # Clear the progress elements
        progress_bar.empty()
        status_text.empty()
        st.rerun()
    
    # Display the jobs view based on mode (list or detail)
    if st.session_state.jobs_loaded:
        if len(st.session_state.ranked_jobs) > 0:
            
            # Job count indicator
            st.success(f"Found {len(st.session_state.ranked_jobs)} matching jobs for you")
            
            # DETAIL VIEW - Show detailed information about selected job
            if st.session_state.view_mode == "detail" and st.session_state.selected_job_id is not None:
                # Back button to return to list view
                if st.button("← Back to Job List", key="back_to_list"):
                    back_to_list()
                
                job_index = st.session_state.selected_job_id
                
                if 0 <= job_index < len(st.session_state.ranked_jobs):
                    current_job = st.session_state.ranked_jobs[job_index]
                    job_details = current_job.get("job_details", {})
                    relevance_score = current_job.get("relevance_score", 0)
                    
                    # Job header section
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"<div class='job-title'>{job_details.get('job_title', 'Job Title')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='company-name'>{job_details.get('employer_name', 'Company')}</div>", unsafe_allow_html=True)
                        
                        # Additional job details
                        job_location = job_details.get('job_city', '') + (', ' + job_details.get('job_country', '') if job_details.get('job_country') else '')
                        if job_location.strip():
                            st.write(f"📍 {job_location}")
                        
                        job_employment_type = job_details.get('job_employment_type', '')
                        if job_employment_type:
                            st.write(f"⏱️ {job_employment_type}")
                            
                        job_salary = job_details.get('job_salary_range', '')
                        if job_salary:
                            st.write(f"💰 {job_salary}")
                    
                    with col2:
                        st.markdown(f"""
                            <div class='relevance-score'>
                                Match Score<br>
                                <span style='font-size: 28px; color: #2e7d32;'>{int(relevance_score * 100)}%</span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Job description
                    st.markdown("<div class='job-description'>", unsafe_allow_html=True)
                    st.markdown(job_details.get('job_description', 'No description available.'))
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Apply button
                    job_apply_link = job_details.get('job_apply_link', '#')
                    st.markdown(f"""
                    <div class='apply-button'>
                        <a href='{job_apply_link}' target='_blank' style='
                            background-color: #4CAF50;
                            color: white;
                            padding: 12px 24px;
                            border: none;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 16px;
                            font-weight: bold;
                            text-decoration: none;
                            display: inline-block;
                        '>
                            Apply Now
                        </a>
                    </div>
                      """, unsafe_allow_html=True)
                    
                    # Navigation buttons between jobs
                    cols = st.columns([1, 8, 1])
                    with cols[0]:
                        if job_index > 0:
                            if st.button("← Previous Job", key="prev_job"):
                                view_job_details(job_index - 1)
                                
                    with cols[2]:
                        if job_index < len(st.session_state.ranked_jobs) - 1:
                            if st.button("Next Job →", key="next_job"):
                                view_job_details(job_index + 1)
                    
                    # Job position indicator
                    st.write(f"Viewing job {job_index + 1} of {len(st.session_state.ranked_jobs)}")
                    
                    # Chatbot section
                    st.subheader("Need help? Chat with JobSphere.AI about this job")
                    
                    # Display current job context
                    st.write(f"Ask questions about the {job_details.get('job_title')} role at {job_details.get('employer_name')}.")
                    
                    # Get chat history for this job
                    if job_index not in st.session_state.chat_histories:
                        st.session_state.chat_histories[job_index] = []
                    chat_history = st.session_state.chat_histories[job_index]
                    
                    # Display chat messages
                    for message in chat_history:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                    
                    # Chat input
                    user_input = st.chat_input("Type your message here...")
                    
                    if user_input:
                        # Add user message to chat history
                        chat_history.append({"role": "user", "content": user_input})
                        
                        # Display user message immediately
                        with st.chat_message("user"):
                            st.markdown(user_input)
                        
                        # Get job description and user preferences
                        with st.spinner("JobSphere.AI is generating a response..."):
                            job_description = job_details.get("job_description", "")
                            user_preferences = st.session_state.user_preferences
                            
                            # Call LLM to get response
                            ai_response = job_details_llm_response(user_input, job_description, user_preferences)
                      
                        
                        # Add AI response to chat history
                        chat_history.append({"role": "assistant", "content": ai_response})
                        
                        # Display assistant response
                        with st.chat_message("assistant"):
                            st.markdown(ai_response)
                else:
                    st.error("Invalid job selection")
                    back_to_list()
            
            # LIST VIEW - Show all jobs in a scrollable list
            else:
                st.subheader("Recommended Jobs")
                
                # Container for job cards
                job_cards_container = st.container()
                
                with job_cards_container:
                    for i, job in enumerate(st.session_state.ranked_jobs):
                        job_details = job.get("job_details", {})
                        relevance_score = job.get("relevance_score", 0)
                        
                        # Create a clickable job card
                        col1, col2 = st.columns([5, 1])
                        
                        card_class = "job-card"
                        if st.session_state.selected_job_id == i:
                            card_class += " selected-job-card"
                            
                        with col1:
                            # Get location string first
                            location_text = ""
                            location_str = job_details.get('job_location', '')
                            if location_str:
                                location_text = location_str
                            else:
                                location_text = job_details.get('job_city', '') + (', ' + job_details.get('job_country', '') if job_details.get('job_country') else '')
                            
                            # The entire column is clickable
                            if st.button(f"##### {job_details.get('job_title', 'Job Title')}\n"
                                      f"#### {job_details.get('employer_name', 'Company')}\n"
                                      f"📍 {location_text}\n",
                                      key=f"job_card_{i}", 
                                      use_container_width=True):
                                view_job_details(i)
                        
                        with col2:
                            st.markdown(f"<div style='text-align:center; padding-top:10px;'><span class='badge score-badge'>Match: {int(relevance_score * 100)}%</span></div>", unsafe_allow_html=True)
                            
                            # Apply button directly in the list
                            job_apply_link = job_details.get('job_apply_link', '#')
                            st.markdown(f"""
                                <div class='apply-button'>
                                    <a href='{job_apply_link}' target='_blank' style='
                                        background-color: #4CAF50;
                                        color: white;
                                        padding: 12px 24px;
                                        border: none;
                                        border-radius: 4px;
                                        cursor: pointer;
                                        font-size: 16px;
                                        font-weight: bold;
                                        text-decoration: none;
                                        display: inline-block;
                                    '>
                                        Apply Now
                                    </a>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        st.divider()
                
                # Reset button at the bottom of the list
                if st.button("Start New Job Search", key="reset_search"):
                    reset_session()
                    
        else:
            # No jobs found
            st.error("No jobs found matching your preferences. Please try with different criteria.")
            if st.button("Try Again"):
                reset_session()
else:
    # Show welcome message when app first loads
    st.write("Welcome to JobSphere! Fill out the form above to find your perfect job match.")