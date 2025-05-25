import json
from serpapi import GoogleSearch
from state import State

SERPAPI_API_KEY = "426ad51c92190895b323f36c127c593afca1ba34c6c00e17a39ef0fcccaa958c"
def fetch_jobs_serpapi(query, location):
    """Fetch job listings using SerpAPI."""
    search_query = f"{query} in {location}"
    print("HELLOOOO")
    params = {
        "engine": "google_jobs",
        "q": search_query,
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("jobs_results", [])

def job_search_api_node(state: State):
    """Job search node that fetches jobs based on user preferences."""
    user_preferences = state["user_preferences"]
    role = user_preferences["role"]
    location_str = user_preferences['location']
    if ',' in location_str:    
        location, country = location_str.split(',')
        location = location.strip()
        country = country.strip()
    else:
        location = location_str
        location = location.strip()
    query = role.strip()
    

    #Fetch jobs using SerpAPI
    jobs_results = fetch_jobs_serpapi(query, location)
    # with open('jobs_data.json', 'r') as file:
    #     jobs_results = json.load(file)

    # Standardize job data for downstream agents
    raw_jobs = []
    for job_id in range(len(jobs_results)):
        job = jobs_results[job_id]
        qualifications = []
        benefits = []
        responsibilities = []
        for highlight in job.get("job_highlights", []):
            title = highlight.get("title", "").lower()
            if title == "qualifications":
                qualifications = highlight.get("items", [])
            elif title == "benefits":
                benefits = highlight.get("items", [])
            elif title == "responsibilities":
                responsibilities = highlight.get("items", [])

        standardized_job = {
            "job_id": job_id, 
            "job_title": job.get("title", ""),
            "employer_name": job.get("company_name", ""),
            "job_description": job.get("description", ""),
            "benefits": benefits,
            "qualifications": qualifications,
            "responsibilities": responsibilities,
            "job_location": job.get("location", ""),
            "job_apply_link": job.get("apply_options", [{}])[0].get("link", "")
        }
        raw_jobs.append(standardized_job)

    with open('jobs_data.json', 'w') as file:
        json.dump(jobs_results, file)
    
    state['raw_jobs'] = raw_jobs
    return state