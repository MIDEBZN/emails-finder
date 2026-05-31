import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scraper import JobSearchClient
from pydantic import BaseModel
from typing import List
from models import JobPosting

app = FastAPI(title="Canadian Job & Email API")

# Add CORS middleware to allow the React frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the live DuckDuckGo scraper
scraper_client = JobSearchClient()

class SearchRequest(BaseModel):
    title: str
    location: str = "Canada"

@app.get("/")
def read_root():
    return {"message": "Canadian Job & Email API is running! Please use the React frontend at http://localhost:5173"}

@app.post("/api/search", response_model=List[JobPosting])
async def search_jobs(request: SearchRequest):
    """
    Endpoint to trigger the live DuckDuckGo and BeautifulSoup scraper.
    """
    jobs = scraper_client.search_jobs(title=request.title, location=request.location)
    return jobs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
