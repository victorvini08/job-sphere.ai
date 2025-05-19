import re
import ollama
import pandas as pd
from flashtext import KeywordProcessor
from state import State

def extract_experience_from_job_description(job_description):
    patterns = [
        r"(\d+)\s*-\s*(\d+)\s*years?",                         # e.g., 3-10 years
        r"(\d+)\s*to\s*(\d+)\s*years?",                        # e.g., 3 to 10 years
        r"(\d+)\+\s*years?",                                   # e.g., 3+ years
        r"(\d+)\s*\+\s*years?",                                # e.g., 3 + years
        r"(\d+)\s*years?",                                     # e.g., 3 years
        r"at least\s*(\d+)\s*years?",                          # e.g., at least 3 years
        r"minimum\s*of\s*(\d+)\s*years?",                      # e.g., minimum of 3 years
        r"requires?\s*(\d+)\s*years?",                         # e.g., requires 3 years
        r"(\d+)\s*years?\s*of\s*(industry\s*)?experience",     # e.g., 3 years of experience
        r"experience\s*of\s*(\d+)\s*years",                    # e.g., experience of 3 years
        r"(\d+)\s*yrs?",                                       # e.g., 3 yrs
        r"(\d+)\s*\+\s*yrs?",                                  # e.g., 3 + yrs
        r"(\d+)\+\s*yrs?",                                     # e.g., 3+yrs
        r"(\d+)\s*yrs?\s*experience",                          # e.g., 3 yrs experience
        r"experience\s*of\s*(\d+)\s*yrs?"                      # e.g., experience of 3 yrs
    ]
    
    extracted_years = []
    for pattern in patterns:
        matches = re.findall(pattern, job_description, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                # If it's a tuple (like from the range patterns), take the first number
                extracted_years.append(match[0])
            else:
                extracted_years.append(match)
    
    years_as_int = []
    for year in extracted_years:
        try:
            years_as_int.append(int(year))
        except (ValueError, TypeError):
            # Skip if we can't convert to integer
            continue
    
    return years_as_int


def extract_skills_from_job_description(job_description: str):
    skills_data = pd.read_csv("./skills_dataset.csv")
    skills_data['Skills'] = skills_data['Skills'].astype('str').str.lower().str.strip()

    skills_list = skills_data['Skills'].drop_duplicates().to_list()

    keyword_processor = KeywordProcessor(case_sensitive=False)
    for skill in skills_list:
        keyword_processor.add_keyword(skill)

    found = keyword_processor.extract_keywords(job_description.lower())
    return list(dict.fromkeys(found))  
    
def filtering_jobs_node(state: State) -> State:
    # Given raw jobs list, find the relevant jobs according to user preferences
    user_preferences = state["user_preferences"]

    user_pref_exp = user_preferences.get("experience", None)
    user_pref_skills = [skill.strip().lower() for skill in user_preferences.get("skills", "").split(",") if skill.strip()]
    user_pref_salary = user_preferences.get("salary", -1)
    user_pref_location = user_preferences.get("location","")  # (Bengaluru, India)


    raw_jobs_list = state['raw_jobs']
    relevant_jobs_list = []
    print("User experience: " + str(user_pref_exp) + ", User skills: " + str(user_pref_skills))
    for i, x in enumerate(raw_jobs_list):
        # First we filter based on experience. We only keep jobs where the user experience is greater than or 
        # to the experience required for the given job
        print("Job number: " + str(i))
        job_description = x['job_description']
        #print('Job description: ' + job_description)
        extracted_years_in_job = extract_experience_from_job_description(job_description)
        print("Experience required for job: " + str(extracted_years_in_job))
        experience_valid = False
        if not extracted_years_in_job:
            experience_valid = True
        else:
            required_experience = max(extracted_years_in_job)
            if user_pref_exp >= required_experience:
                experience_valid = True
            
        if experience_valid is False:
            continue
    
        # Then we filter based on the skills. We find the relevant skills required from the job description. 
        # We only keep the jobs which has atleast some intersection with the user's skills
        skills_in_job_description = extract_skills_from_job_description(job_description)
        print("Skills required for job: " + str(skills_in_job_description))
        if (set(user_pref_skills) & set(skills_in_job_description)) == False:
            continue
        relevant_jobs_list.append(x)
    print('Relevant jobs list length: ' + str(len(relevant_jobs_list)))
    state['relevant_jobs'] = relevant_jobs_list    
    return state
