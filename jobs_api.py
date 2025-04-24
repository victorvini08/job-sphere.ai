import requests
import json

url = "https://jsearch.p.rapidapi.com/search"

querystring = {"query":"software engineer jobs in MNCs at bangalore","page":"1","num_pages":"1","country":"IN","date_posted":"all"}

headers = {
	"x-rapidapi-key": "de07073447msh364f14163b92444p1fb8f4jsn4f742edaf713",
	"x-rapidapi-host": "jsearch.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

jobs_list = response.json()

with open('jobs_data.json', 'w') as file:
    json.dump(jobs_list, file)
