import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'api'))
from scraper import JobSearchClient

client = JobSearchClient()

jobs_page_1 = client.search_jobs('Developer', 'Canada', max_results=10, start_offset=0)
jobs_page_2 = client.search_jobs('Developer', 'Canada', max_results=10, start_offset=10)

print(f"Page 1: {[j.title for j in jobs_page_1]}")
print(f"Page 2: {[j.title for j in jobs_page_2]}")

if len(jobs_page_1) > 0 and len(jobs_page_2) > 0:
    if jobs_page_1[0].title == jobs_page_2[0].title and jobs_page_1[0].company == jobs_page_2[0].company:
        print("\nDUPLICATE DETECTED!")
    else:
        print("\nDIFFERENT RESULTS.")
