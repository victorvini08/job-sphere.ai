import re
import ollama
import pandas as pd
from utils import summarize_job_using_llm, extract_experience_years, extract_skills_from_job_description
from state import State

def filtering_jobs_node(state: State) -> State:
    # Given raw jobs list, find the relevant jobs according to user preferences
    skills_threshold = 1
    user_preferences = state["user_preferences"]
    user_pref_exp = user_preferences.get("experience", None)
    user_pref_skills = [skill.strip().lower() for skill in user_preferences.get("skills", "").split(",") if skill.strip()]

    raw_jobs_list = state['raw_jobs']
    relevant_jobs_list = []
    job_summaries = {}
    print("User experience: " + str(user_pref_exp) + ", User skills: " + str(user_pref_skills))
    for i, x in enumerate(raw_jobs_list):
        print("Job number: " + str(i))
        job_description = x['job_description']       
        responsibilities_str = ', '.join(x['responsibilities'])
        benefits_str = ', '.join(x['benefits'])

        # Then we filter based on the skills. We find the relevant skills required from the job description. 
        # We only keep the jobs which has  ntersection with the user's skills of atleast skills_threshold 
        skills_in_job_description = extract_skills_from_job_description((job_description+responsibilities_str))
        print("Skills required for job: " + str(skills_in_job_description))
        intersection = len(set(user_pref_skills) & set(skills_in_job_description))
        print(f"Intersection between skills: {intersection}")
        if intersection < skills_threshold:
            continue

        
        job_summary = summarize_job_using_llm(job_description, benefits_str)
        job_summary = job_summary + " Job Location: " + x["job_location"]
        exp_in_years = extract_experience_years(job_summary)
        print("Experience required for job: " + str(exp_in_years))
        if(user_pref_exp < exp_in_years):
            continue
        job_summaries[x['job_id']] = job_summary
        relevant_jobs_list.append(x)
    print('Relevant jobs list length: ' + str(len(relevant_jobs_list)))
    state['relevant_jobs'] = relevant_jobs_list    
    state['job_summaries'] = job_summaries
    return state
