from fastapi import APIRouter

from app.api.schemas import AnalyzeRequest, AnalyzeResponse
from app.llm import extract_job_requirements
from app.matcher import match_skills
from app.profile_loader import load_profile
from pathlib import Path


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_job(request: AnalyzeRequest) -> AnalyzeResponse:
    profile = load_profile(
        Path("data/profile.json")
    )

    requirements = extract_job_requirements(
        request.job_description
    )

    matching_skills, missing_skills = match_skills(
        profile,
        requirements,
    )

    return AnalyzeResponse(
        required_skills=requirements.required_skills,
        preferred_skills=requirements.preferred_skills,
        responsibilities=requirements.responsibilities,
        keywords=requirements.keywords,
        matching_skills=sorted(matching_skills),
        missing_required_skills=sorted(missing_skills),
    )