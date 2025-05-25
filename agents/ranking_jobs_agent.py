from state import State
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils import stringify_user_preferences

def find_similarity(job_summary, user_preferences_str):

    similarity_model = SentenceTransformer('BAAI/bge-large-en-v1.5')

    # Generate embeddings
    user_pref_embedding = similarity_model.encode(user_preferences_str)
    job_summary_embedding = similarity_model.encode(job_summary)
    
    # Calculate similarity score
    return float(cosine_similarity([user_pref_embedding], [job_summary_embedding])[0][0])

def ranking_jobs_node(state: State) -> State:
    # Given relevant jobs list, find the ranked jobs according to user preferences
    user_preferences = state["user_preferences"]
    job_summaries = state["job_summaries"]
    user_preferences_str = stringify_user_preferences(user_preferences)

    relevant_jobs = state['relevant_jobs']
    ranked_jobs_list = []
    for job in relevant_jobs:
        job_id = job['job_id']
        job_summary = job_summaries[job_id]
        relevance_score = find_similarity(job_summary, user_preferences_str)
        ranked_job = {'job_details': job, "relevance_score": relevance_score}
        ranked_jobs_list.append(ranked_job)
    ranked_jobs_list.sort(key=lambda x: x['relevance_score'], reverse=True)
    print(ranked_jobs_list)
    state['ranked_jobs'] = ranked_jobs_list
    
    return state
