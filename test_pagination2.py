import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'api'))
from scraper import JobSearchClient
import requests

client = JobSearchClient()

params = {
    "engine": "google_jobs",
    "q": "Developer Canada",
    "hl": "en",
    "gl": "ca", # Enforce Canada geolocation
    "google_domain": "google.ca",
    "api_key": client.api_key,
    "start": 0
}

response = requests.get(client.base_url, params=params)
data = response.json()

print(data.keys())
if 'serpapi_pagination' in data:
    print("Pagination Info:", data['serpapi_pagination'])
else:
    print("No serpapi_pagination found.")
