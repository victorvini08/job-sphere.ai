from state import State

def filtering_jobs_node(state: State) -> State:
    # Given raw jobs list, find the relevant jobs according to user preferences
    user_preferences = state["user_preferences"]

    user_pref_role = user_preferences.get("role", "").lower()
    user_pref_exp = user_preferences.get("experience", None).lower()
    user_pref_skills = user_preferences.get(
        [skill.strip().lower() for skill in user_preferences.get("skills", "").split(",") if skill.strip()])
    user_pref_salary = user_preferences.get("salary", -1)
    user_pref_location = user_preferences.get(
        [location.strip().lower() for location in user_preferences.get("location", "").split(",") if
         location.strip()])  # (Bengaluru, India)
    user_pref_company_size = user_preferences.get("company_size", "").lower()
    user_pref_company_desc_keywords = user_preferences.get(
        [keyword.strip().lower() for keyword in user_preferences.get("company_description", "").split(",") if
         keyword.strip()])

    pass
