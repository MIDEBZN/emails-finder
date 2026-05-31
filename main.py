import argparse
from rich.console import Console
from rich.table import Table
from scraper import JobSearchClient

console = Console()

def print_jobs_table(jobs):
    table = Table(title="Canadian Job Search Results", show_header=True, header_style="bold magenta")
    
    table.add_column("Job Title", style="cyan", no_wrap=True)
    table.add_column("Company", style="blue")
    table.add_column("Location", style="green")
    table.add_column("Found Emails", style="yellow")
    
    for job in jobs:
        emails_str = ", ".join([e.email for e in job.emails]) if job.emails else "None found"
        table.add_row(job.title, job.company, job.location, emails_str)
        
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Canadian Job & Email Aggregation System")
    parser.add_argument("--title", type=str, required=True, help="Job title to search for (e.g. 'Software Engineer')")
    parser.add_argument("--location", type=str, default="Canada", help="Geographic location (e.g. 'Toronto', 'BC')")
    
    args = parser.parse_args()
    
    client = JobSearchClient()
    
    with console.status(f"[bold green]Searching for {args.title} jobs in {args.location}..."):
        jobs = client.search_jobs(title=args.title, location=args.location)
    
    if not jobs:
        console.print(f"[bold red]No jobs found for {args.title}.[/bold red]")
        return
        
    print_jobs_table(jobs)
    
    console.print(f"\n[bold blue]Found {len(jobs)} jobs. Extracted {sum(len(j.emails) for j in jobs)} emails.[/bold blue]")

if __name__ == "__main__":
    main()
