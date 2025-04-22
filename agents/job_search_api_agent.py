import pycountry
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


def job_search_api_node(state: State):
    user_preferences = state["user_preferences"]
    role = user_preferences["role"]
    loc_country = user_preferences["location"].split(',')
    location, country = loc_country[0], loc_country[1]
    query = f"{role} jobs in {location}"
    query_string = {"query":"software engineer jobs in MNCs at bangalore","page":"1","num_pages":"1","country":"in","date_posted":"all"}

    #list_jobs = fetch_jobs_jsearch_api(query_string)
