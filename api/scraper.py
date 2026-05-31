import requests
from typing import List
from models import JobPosting
from email_extractor import extract_emails_from_text

class JobSearchClient:
    def __init__(self, api_key: str = "775a1e0b64dc6f8afa85e37d43bf7e325d7b709839a6e0d59507be2ce4253a07"):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search.json"

    def search_jobs(self, title: str, location: str = "Canada", max_results: int = 10) -> List[JobPosting]:
        """
        Uses SerpApi (Google Jobs engine) to find highly accurate job postings in Canada.
        """
        jobs = []
        
        params = {
            "engine": "google_jobs",
            "q": f"{title} {location}",
            "hl": "en",
            "gl": "ca", # Enforce Canada geolocation
            "google_domain": "google.ca",
            "api_key": self.api_key
        }
        
        try:
            # Fetch up to max_results jobs from SerpApi. Cap at 50 to avoid Vercel timeouts.
            capped_max = min(max_results, 50)
            for start in range(0, capped_max, 10):
                params["start"] = start
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                job_results = data.get("jobs_results", [])
                if not job_results:
                    break # No more pages available
                
                for res in job_results:
                    job_title = res.get("title", title)
                    company = res.get("company_name", "Unknown Company")
                    job_location = res.get("location", location)
                    description = res.get("description", "")
                    
                    # Get the best available link
                    url = "#"
                    related_links = res.get("related_links", [])
                    if related_links:
                        url = related_links[0].get("link", "#")
                    else:
                        url = res.get("share_link", "#")
                    
                    job = JobPosting(
                        title=job_title,
                        company=company,
                        location=job_location,
                        description=description,
                        url=url
                    )
                    
                    # Extract emails directly from the Google Jobs description text
                    found_emails = extract_emails_from_text(description)
                    for email in found_emails:
                        if "no-reply" not in email and "sentry" not in email:
                            job.add_email(email=email, source="Job Description", confidence=0.90)
                            
                    # Try deep scraping the actual link to find raw emails hidden on the site
                    try:
                        if url != "#" and "google" not in url:
                            import urllib3
                            urllib3.disable_warnings()
                            page_resp = requests.get(url, timeout=4, verify=False, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                            if page_resp.status_code == 200:
                                # Scan the raw HTML code (page_resp.text) to catch hidden 'mailto:' links,
                                # JSON configurations, and script-rendered emails that get lost when stripping tags.
                                deep_emails = extract_emails_from_text(page_resp.text)
                                
                                for email in deep_emails:
                                    # Ensure it's unique
                                    if not any(e.email == email for e in job.emails):
                                        job.add_email(email=email, source="Deep HTML Scrape", confidence=0.85)
                    except Exception:
                        pass
                        
                    # If no emails found at all via deep scrape, query Hunter.io's massive B2B database
                    if len(job.emails) == 0 and company != "Unknown Company":
                        try:
                            hunter_url = "https://api.hunter.io/v2/domain-search"
                            hunter_params = {
                                "company": company,
                                "api_key": "ddab7b7c51c926e33b368e051b10877024620676",
                                "limit": 3 # Get top 3 verified emails
                            }
                            hunter_resp = requests.get(hunter_url, params=hunter_params, timeout=4)
                            if hunter_resp.status_code == 200:
                                hunter_data = hunter_resp.json()
                                emails_list = hunter_data.get("data", {}).get("emails", [])
                                for e_obj in emails_list:
                                    hunter_email = e_obj.get("value")
                                    hunter_conf = float(e_obj.get("confidence", 80)) / 100.0
                                    # Ensure it's unique
                                    if hunter_email and not any(e.email == hunter_email for e in job.emails):
                                        job.add_email(email=hunter_email, source="Hunter.io Verified", confidence=hunter_conf)
                        except Exception as e:
                            pass # Skip if Hunter fails or rate limits
                            
                    jobs.append(job)
                    
                    if len(jobs) >= max_results:
                        break # Stop if we reached the requested max_results
                
                if len(jobs) >= max_results:
                    break
                
        except Exception as e:
            print(f"SerpApi Search failed: {e}")
            
        # Fallback if no jobs were found (e.g. invalid API key or network error)
        if not jobs:
            print(f"No live results found for {title} in {location}. Using fallback data for demonstration.")
            mock_jobs = [
                JobPosting(
                    title=f"Senior {title}",
                    company="TechCorp Canada",
                    location=location,
                    description=f"We are looking for a Senior {title}. Please send your resume to careers@techcorp.ca or contact our recruiter at sarah.smith@techcorp.ca.",
                    url="https://techcorp.ca/careers"
                )
            ]
            for job in mock_jobs:
                found_emails = extract_emails_from_text(job.description)
                for email in found_emails:
                    job.add_email(email=email, source="Fallback Data", confidence=0.99)
            return mock_jobs

        return jobs
