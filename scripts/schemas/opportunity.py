from typing import Optional

from pydantic import BaseModel, validator


class Opportunity(BaseModel):
    title: str
    agency: str
    description: str = ""
    value: float = 0.0
    currency: str = "USD"
    close_date: Optional[str] = None
    url: str
    source: str
    country: str = "Global"
    segment: str = "DaaS"
    dna_score: int = 0
    urgency: int = 50

    @validator("description", pre=True)
    def clean_desc(cls, v):
        return (v or "")[:5000]
