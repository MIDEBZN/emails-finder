from pydantic import BaseModel, Field
from typing import List, Optional

class ExtractedEmail(BaseModel):
    email: str
    source: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    emails: List[ExtractedEmail] = []
    
    def add_email(self, email: str, source: str, confidence: float):
        self.emails.append(ExtractedEmail(email=email, source=source, confidence=confidence))
