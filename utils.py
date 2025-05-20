import ollama 

def job_details_llm_response(user_query: str, job_description: str, user_preferences):

    prompt = f"""You are an AI assistant helping with job-related queries. 
                 Here is the job description: {job_description}.
                 The user asked below question: {user_query}. Please provide a concise response answering the user's query regarding the job details. Directly give the answer to the query as response nothing else."""
    
    response = ollama.chat(
        model="gemma3:1b", 
        messages=[
            {"role": "system", "content": "You are an expert at answering job-related queries."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content']

# job_desc = """Job Title- Senior AI Engineer\n\nPosition type- Full Time\n\nARL - 5.1\n\nWork Location- Bangalore, Noida, Gurgaon (Hybrid)\n\nWorking style- Hybrid\n\nCab Facility- Yes\n\n
# Shift Time \u2013 12 pm-9 pm IST\n\nPeople Manager role: No\n\nRequired education and certifications critical for the role - Bachelor's or Master's degree in Computer Science, Engineering, or a related field.\n\n
# Required years of experience \u2013\n\n10-14 years\u2019 experience in relevant field\n\nAON IS IN THE BUSINESS OF BETTER DECISIONS\n\nAt Aon, we shape decisions for the better to protect and enrich the lives of people around the world.\n\nAs an organization, we are committed to our purpose as one firm, united through trust as one inclusive, diverse team and we are passionate about helping our colleagues and clients succeed.\n\nGENERAL DESCRIPTION OF ROLE:\n\nWe are seeking a senior AI Engineer with a strong background in Data Engineering or Machine Learning to join our team focused on building AI-driven solutions. The role is ideal for someone to experience both model development and system integration using cloud native AI services. Knowledge of API development and understanding of UI/UX is an added advantage.\n\nWhat the day will look like:\n\u2022 Design and implement AI solutions using Azure OpenAI, AWS Bedrock or other cloud native services\n\u2022 Build scalable data pipelines, pre-process large datasets and generate vector embeddings or semantic search\n\u2022 Experiment with LLM, RAG and agent-based orchestration framework\n\u2022 Collaborate with cross functional team including product, data and engineering team to shape AI capabilities\n\u2022 Proactively identify areas of model hallucination or bias and implement mitigation\n\u2022 Develop AI services, 
# contribute UX design discussion or better model-human interaction\n\u2022 Participate in agile ceremonies, code reviews and continuous learning.\n\n
# Key Responsibilities:\n\u2022 Implement end to end AI solution: data ingestion, pre-processing, training and deployment\n\u2022 Utilize cloud Ai services (Azure/AWS) for model deployment, fine tuning and orchestration\n\u2022 Build and maintain API services using C#, Python\n\u2022 Design and maintain vector database and embedding pipelines using tools like Pinecone, FAISS etc.\n\u2022 Implement model evaluation metrics, dashboards, and monitoring tools to detect drift and hallucinations\n\u2022
#  Ensure security, scalability, performance in AI solution delivery\n\nSkills/competencies required:\n\u2022 10+ years of total experience, including 3-5 years in AI/ML or data Engineering\n\u2022 Strong programming skills in Python, 
# with experience in ML libraries like PyTorch or TensorFlow\n\u2022 Experience in developing and deploying AI solutions using Azure, AWS services\n\u2022
#  Proficient in model lifecycle management\n\u2022 Familiarity of LLM orchestration, 
# RAG pipelines and multi-agent system\n\u2022 Comfortable in API design, preferably using C# or Python (Flask/fast API)\n\u2022 Exposure to agent framework like LangChain, CrewAI etc.\n\u2022 Cloud native development experience using AWS Lambda, SageMaker pipeline\n\u2022 Understanding of Responsible AI principals, bias detection, ad mitigation strategies.\n\nHow this opportunity is different \u2013\n\u2022 Work with cutting edge AI Models and API\n\u2022 Opportunity to learn and grow into AI architecture role\n\u2022 Direct impact on AI-powered application- real world AI automation and integration\n\u2022 Cross functional learning- GenAI, data engineering, and API development\n\u2022 Collaborate directly with leadership involved in shaping AI product vision- making strategical impact\n\nHOW WE SUPPORT OUR COLLEAGUES\n\nIn addition to our comprehensive benefits package, we are proud to be an equal opportunity workforce. At Aon, we believe a diverse workforce is an innovative workforce. Our agile, inclusive environment allows colleagues to manage their wellbeing and work/life balance while empowering you to be your authentic self.\n\nFurthermore, all colleagues enjoy two \u201cGlobal Wellbeing Days\u201d each year, encouraging them to take time to focus on themselves. We offer a variety of workstyle options through our Smart Working model, but we also recognize that flexibility goes beyond just the place of work... and we are all for it!\n\nOur continuous learning culture inspires and equips colleagues to learn, share and grow, helping them achieve their fullest potential. As a result, Aon colleagues are more connected, more relevant and more valued.\n\nCOMMITMENT TO SUSTAINABILITY\n\n\u201cAon is dedicated to integrating sustainability into our core business practices. We strive to minimize our environmental impact through innovative solutions and responsible stewardship, ensuring a sustainable future for our clients and communities.\u201d\n\n#LI-SN1\n\n2561761""",
# user_preferences = {
#     "role": "Software Engineer",
#     "experience": 3,
#     "skills": 'Python, Django, REST APIs, AWS, SQL',
#     "salary": "10-15 LPA",
#     "location": "Bangalore, India",
#     "company_size": "200 employees",
#     "company_description": "Innovative, AI expert"
# }        
# answer = job_details_llm_responses('What are the qualifications required for the job?',job_desc, user_preferences)
# print(answer)