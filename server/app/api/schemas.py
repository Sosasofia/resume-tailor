from pydantic import BaseModel
from typing import Literal

from app.domain.models import JobRequirements
from app.domain.profile import ResumeProfile


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


class TailorResponse(BaseModel):
    format: Literal["markdown", "pdf"]


class ValidationIssueResponse(BaseModel):
    section: str
    claim: str
    reason: str


class TailorValidationErrorResponse(BaseModel):
    stage: Literal[
        "deterministic_factuality",
        "semantic_factuality",
    ]
    errors: list[str] = []
    issues: list[ValidationIssueResponse] = []