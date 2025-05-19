import numpy as np
import torch
import ollama
import json
import re
from state import State
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.metrics.pairwise import cosine_similarity

def sort_with_indices(my_list):
    # Create a list of (index, value) tuples
    indexed_list = list(enumerate(my_list))

    # Sort the list based on the values (second element of the tuple) in descending order
    indexed_list.sort(key=lambda x: x[1], reverse=True)

    return indexed_list

def jsonify_job_description(job_description):
    prompt = f"""
    Extract the following from the job description as a JSON object. Use null for missing fields and empty lists for skills/company_points if none are specified.
    Only include text from the job description don't include anything extra
    - Role: Job title (e.g., Software Engineer)
    - Location: Job location (e.g., "Bangalore, India", null if unspecified)
    - Skills: List of skills (e.g., ["Python", "Java"], [] if none)
    - Experience: Years required (e.g., "3-5 years", null if unspecified)
    - Salary: Salary/range (e.g., "10-15 LPA", null if unspecified)
    - Company Points: Company characteristics / Summary

    Job Description:
    {job_description}

    Output:
    JSON with below keys:
      "role",
      "location",
      "skills",
      "experience",
      "salary",
      "company_points"
    """

    response = ollama.chat(
        model="llama3", 
        messages=[
            {"role": "system", "content": "You are an expert at extracting structured information from text in JSON format."},
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": 0.0,
            "format": "json"  # Enforce JSON output
        }
    )
    print(response['message']['content'])
    match = re.search(r'```(.*?)```', response['message']['content'], re.DOTALL)
    if not match:
        raise ValueError("No JSON content found in the response")

    json_string = match.group(1)
    return json_string

def find_similarity(queries, job_descriptions):

    similarity_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
    json_jobs_list = []
    for job_description in job_descriptions:
        json_job = jsonify_job_description(job_description)
        json_jobs_list.append(json_job)
    # Generate embeddings
    query_embeddings = similarity_model.encode([str(queries)])
    relevant_text_embeddings = similarity_model.encode(job_descriptions)
    
    # Calculate similarity matrix
    similarity_scores = cosine_similarity(query_embeddings, relevant_text_embeddings)

   
    return similarity_scores

def ranking_jobs_node(state: State) -> State:
    # Given relevant jobs list, find the ranked jobs according to user preferences
    user_preferences = state["user_preferences"]

    user_pref_role = user_preferences.get("role", "").lower()
    user_pref_exp = user_preferences.get("experience", None)
    user_pref_skills = [skill.strip().lower() for skill in user_preferences.get("skills", "").split(",") if skill.strip()]
    user_pref_salary = user_preferences.get("salary", -1)
    user_pref_location = user_preferences.get("location","")  # (Bengaluru, India)
    #user_pref_company_size = user_preferences.get("company_size", "").lower()
    user_pref_company_desc_keywords = [keyword.strip().lower() for keyword in user_preferences.get("company_description", "").split(",") if
         keyword.strip()]

    query_templates = [
    "The job is for a {role}.",
    "The job is located in {location}.",
    "The job requires skills in {skills}.",
    "The job requires {experience} years of experience.",
    "The job will provide {salary} expected salary",
    "The company is {company_description}."
    ]
    queries = {
    "role": query_templates[0].format(role=user_pref_role),
    "location": query_templates[1].format(location=user_pref_location),
    "skills": query_templates[2].format(skills=", ".join(user_pref_skills)),
    "experience": query_templates[3].format(experience=user_pref_exp),
    "salary": query_templates[4].format(salary=user_pref_salary),
    "company_description": query_templates[5].format(company_description= ", ".join(user_pref_company_desc_keywords))
    }

    relevant_jobs = state['relevant_jobs']
    job_descriptions = [(x["job_description"] + "Job Location: " + x["job_location"]) for x in relevant_jobs]

    similarity_matrix = find_similarity(queries, job_descriptions)
    relevance_scores = (similarity_matrix[0]).tolist()
    rankings = sort_with_indices(relevance_scores)
    ranked_jobs_list = []
    for rank_tuple in rankings:
        job_index = rank_tuple[0]
        relevance_score = rank_tuple[1]
        ranked_job = {'job_details': relevant_jobs[job_index], "relevance_score": relevance_score}
        ranked_jobs_list.append(ranked_job)
    print(ranked_jobs_list)
    state['ranked_jobs'] = ranked_jobs_list
    
    return state
