import re
from typing import List

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

def extract_emails_from_text(text: str) -> List[str]:
    """
    Scans a block of text (like a job description or raw HTML) for email addresses.
    Returns a list of unique email addresses found.
    """
    if not text:
        return []
    emails = EMAIL_REGEX.findall(text)
    
    valid_emails = []
    invalid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.svg', '.webp', 'sentry', 'no-reply', 'noreply', 'example')
    
    for email in emails:
        email = email.lower()
        # Filter out common false positives from raw HTML
        if not any(ext in email for ext in invalid_extensions):
            valid_emails.append(email)
            
    # Deduplicate
    return list(set(valid_emails))
