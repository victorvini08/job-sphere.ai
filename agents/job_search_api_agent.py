import pycountry
import requests
from state import State

def get_country_iso2(country_name):
    country = pycountry.countries.get(name=country_name)
    if country:
        return country.alpha_2
    else:
        # Try alternative lookup if exact match not found
        try:
            return pycountry.countries.search_fuzzy(country_name)[0].alpha_2
        except LookupError:
            return None

def fetch_jobs_jsearch_api(query_string):
    url = "https://jsearch.p.rapidapi.com/search"


    headers = {
        "x-rapidapi-key": "de07073447msh364f14163b92444p1fb8f4jsn4f742edaf713",
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=query_string)

    jobs_json = response.json()
    if jobs_json['status'] == "OK":
        return jobs_json['data']
    else:
        raise Exception("Error occured in API call")

def job_search_api_node(state: State):
    print(state)
    user_preferences = state["user_preferences"]
    role = user_preferences["role"]
    loc_country = user_preferences["location"].split(',')
    location, country = loc_country[0], loc_country[1]
    query = f"{role} jobs in {location}"
    country_code = get_country_iso2(country)
    experience = user_preferences['experience']
    exp_string = ""
    if experience == 0:
        exp_string = "no_experience"
    elif experience <= 3:
        exp_string = "under_3_years_experience"
    else:
        exp_string = "more_than_3_years_experience"
    
    query_string = {"query":query,"page":"1","num_pages":"1","country":country_code,
                    "date_posted":"all","job_requirements": exp_string}

    list_jobs = fetch_jobs_jsearch_api(query_string)

    state['raw_jobs'] = list_jobs

    return state
