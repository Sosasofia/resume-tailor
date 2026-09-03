from typing import Literal

from app.models import JobRequirements
from app.profile import ResumeProfile
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    job_description: str


class AnalyzeResponse(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    keywords: list[str]
    matching_skills: list[str]
    missing_required_skills: list[str]
    

class ExtractResponse(BaseModel):
    document_type: Literal["resume", "job_description"]
    data: JobRequirements | ResumeProfile