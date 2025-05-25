import ollama 
import re
from flashtext import KeywordProcessor
import pandas as pd

def stringify_user_preferences(user):
    return f"""
        Role: {user['role']}
        Experience: {user['experience']} years
        Skills: {user['skills']}
        Salary Expectation: {user['salary']}
        Preferred Location: {user['location']}
        Company Type: {user['company_description']}
        """

def job_details_llm_response(user_query: str, job_description: str):

    prompt = f"""You are an AI assistant helping with job-related queries. 
                 Here is the job description: {job_description}.
                 The user asked below question: {user_query}. Please provide a concise response answering the user's query regarding the job details. Directly give the answer to the query as response nothing else."""
    
    response = ollama.chat(
        model="gemma3:1b", 
        messages=[
            {"role": "system", "content": "You are an expert at answering job-related queries."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content']

def summarize_job_using_llm(job_description, job_benefits):
    prompt = f"""You are an AI assistant with an expertise in extracting relevant data from a given job description. 
                 Here is the job description: {job_description}.
                 Also, to extract salary, use below job benefits text: {job_benefits}.
                 Extract the relevant data from the job description as follows: 
                 1. Role 
                 2. Experience in years required for the job
                 3. Skills Required 
                 4. Salary 
                 5. Company Highlights. 
                 Only provide this data if present in the job description otherwise put them as null."""
        
    response = ollama.chat(
        model="gemma3:1b", 
        messages=[
            {"role": "system", "content": "You are an expert at answering queries about job descriptions."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content']

def extract_experience_years(full_text):
    experience_line_match = re.search(r'\*\*Experience.*?:\*\* (.+)', full_text)
    if not experience_line_match:
        return 0  # Experience not found

    experience_text = experience_line_match.group(1)

    # Step 2: Extract the first number (usually the lower bound)
    numbers = re.findall(r'\d+', experience_text)
    if numbers:
        return int(numbers[0])  # Return the minimum experience
    return 0

def extract_skills_from_job_description(job_description: str):
    skills_data = pd.read_csv("./skills_dataset.csv")
    skills_data['Skills'] = skills_data['Skills'].astype('str').str.lower().str.strip()

    skills_list = skills_data['Skills'].drop_duplicates().to_list()

    keyword_processor = KeywordProcessor(case_sensitive=False)
    for skill in skills_list:
        keyword_processor.add_keyword(skill)

    found = keyword_processor.extract_keywords(job_description.lower())
    return list(dict.fromkeys(found))  