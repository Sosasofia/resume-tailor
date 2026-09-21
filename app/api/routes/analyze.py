from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.domain.models import ResumeAnalysis
from app.services.input import (
    InputValidationError,
    resolve_job_requirements,
    resolve_profile,
)
from app.services.matching import build_resume_analysis


router = APIRouter(
    tags=["analyze"],
)


@router.post(
    "/analyze",
    response_model=ResumeAnalysis,
)
async def analyze(
    resume: UploadFile | None = File(None),
    profile_json: str | None = Form(None),
    job_description: UploadFile | None = File(None),
    job_description_text: str | None = Form(None),
    job_requirements_json: str | None = Form(None),
) -> ResumeAnalysis:
    try:
        resume_content = (
            await resume.read()
            if resume is not None
            else None
        )

        profile = resolve_profile(
            profile_json=profile_json,
            resume_filename=(
                resume.filename
                if resume is not None
                else None
            ),
            resume_content=resume_content,
        )

        job_description_content = (
            await job_description.read()
            if job_description is not None
            else None
        )

        requirements = resolve_job_requirements(
            job_description_filename=(
                job_description.filename
                if job_description is not None
                else None
            ),
            job_description_content=job_description_content,
            job_description_text=job_description_text,
            job_requirements_json=job_requirements_json,
        )

    except InputValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=exc.detail,
        ) from exc

    return build_resume_analysis(
        profile,
        requirements,
    )