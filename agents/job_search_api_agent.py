import json
from serpapi import GoogleSearch
from state import State

def fetch_jobs_serpapi(query, location, country):
    """Fetch job listings using SerpAPI."""
    search_query = f"{query} in {location}"
    params = {
        "engine": "google_jobs",
        "q": search_query,
        "hl": "en",
        "api_key": "426ad51c92190895b323f36c127c593afca1ba34c6c00e17a39ef0fcccaa958c"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("jobs_results", [])

def job_search_api_node(state: State):
    """Job search node that fetches jobs based on user preferences."""
    user_preferences = state["user_preferences"]
    role = user_preferences["role"]
    location, country = user_preferences["location"].split(',')
    query = role.strip()
    location = location.strip()
    country = country.strip()

    # Fetch jobs using SerpAPI
    jobs_results = fetch_jobs_serpapi(query, location, country)

    # Standardize job data for downstream agents
    raw_jobs = []
    for job in jobs_results:
        standardized_job = {
            "job_title": job.get("title", ""),
            "employer_name": job.get("company_name", ""),
            "job_description": job.get("description", ""),
            "job_location": job.get("location", ""),
            "job_apply_link": job.get("apply_options", [{}])[0].get("link", "")
        }
        raw_jobs.append(standardized_job)

    # Save to file for debugging (optional)
    with open('jobs_data.json', 'w') as file:
        json.dump(raw_jobs, file)
    
    state['raw_jobs'] = raw_jobs
    return state