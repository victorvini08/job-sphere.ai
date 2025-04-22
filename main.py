import streamlit as st
from graph import create_graph

compiled_graph = create_graph()

st.title("JobSphere: Your AI-Powered Job Search Assistant")

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {}

if not st.session_state.form_submitted: 
    with st.form(key='user_preferences_form'):
        st.subheader('Please provide your job preferences below')

        role = st.text_input("Desired Role",placeholder="eg. Software Engineer")

        experience = st.number_input("Experience",placeholder='Years of Experience', value=None)

        skills = st.text_area("Skills", placeholder="List your skills, separated by commas")
        
        salary = st.number_input("Minimum Salary Expectation (in INR)", min_value=0, step=100000)
        
        location = st.text_input("Location", placeholder="Preferred country/location for job")
        company_size_options = ["Startup", "Small/Medium Enterprise", "MNC", "Any"]
        company_size = st.selectbox("Preferred Company Size", company_size_options)
        
        company_description = st.text_area("Desired Company Attributes (Optional)", placeholder="e.g., innovative, remote-friendly")
        
        submit_button = st.form_submit_button(label="Submit")
        
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
            st.rerun()

# Display the chatbot interface if form is submitted
if st.session_state.form_submitted:
    
    with st.spinner("Fetching and processing job listings..."):
        final_state = compiled_graph.invoke({"user_preferences": st.session_state.user_preferences})

    st.subheader("Chat with JobSphere.AI")
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate AI response (placeholder)
        ai_response = "I'm here to help you find your job! How can I assist you today?"
        
        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # Rerun to update the chat
        st.rerun()

    
