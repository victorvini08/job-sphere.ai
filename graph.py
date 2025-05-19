from state import State
from langgraph.graph import END, StateGraph
from agents.job_search_api_agent import job_search_api_node
from agents.filtering_jobs_agent import filtering_jobs_node
from agents.ranking_jobs_agent import ranking_jobs_node

#DUMMY USER PREFERENCES
user_preferences = {
    "role": "Software Engineer",
    "experience": 3,
    "skills": 'Python, Django, REST APIs, AWS, SQL',
    "salary": "10-15 LPA",
    "location": "Bangalore, India",
    "company_size": "200 employees",
    "company_description": "Innovative, AI expert"
}

def create_graph():
    graph = StateGraph(State)
    agents = {
        "JobSearchAgent": job_search_api_node, 
        "FilteringAgent": filtering_jobs_node, 
        "RankingAgent": ranking_jobs_node
    }
    for agent_name in agents.keys(): 
        graph.add_node(agent_name, agents[agent_name])

    graph.add_edge('JobSearchAgent', 'FilteringAgent')
    graph.add_edge('FilteringAgent', 'RankingAgent')
    graph.add_edge('RankingAgent', END)
    graph.set_entry_point('JobSearchAgent')

    print("Graph has been created")
    return graph.compile()


# graph = create_graph()
# graph.invoke({"user_preferences": user_preferences})