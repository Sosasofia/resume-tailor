import json
from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.domain.models import JobRequirements, ResumeAnalysis
from app.domain.profile import ResumeProfile
from app.documents.parser import extract_pdf_text
from app.services import extraction
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
    resume_sources = sum(
        source is not None
        for source in (
            resume,
            profile_json,
        )
    )

    if resume_sources != 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "Exactly one resume source is required: "
                "'resume' or 'profile_json'."
            ),
        )

    job_sources = sum(
        source is not None
        for source in (
            job_description,
            job_description_text,
            job_requirements_json,
        )
    )

    if job_sources != 1:
        raise HTTPException(
            status_code=400,
            detail=(
                "Exactly one job source is required: "
                "'job_description', 'job_description_text', "
                "or 'job_requirements_json'."
            ),
        )

    if profile_json is not None:
        try:
            profile = ResumeProfile.model_validate(
                json.loads(profile_json)
            )
        except (json.JSONDecodeError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail="profile_json is not valid ResumeProfile JSON.",
            ) from exc

    else:
        assert resume is not None

        if not (resume.filename or "").lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Resume uploads must currently be PDF files.",
            )

        content = await resume.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded resume is empty.",
            )

        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            temp_path.write_bytes(content)
            resume_text = extract_pdf_text(temp_path)
            profile = extraction.extract_resume_profile(resume_text)
        finally:
            temp_path.unlink(missing_ok=True)

    if job_requirements_json is not None:
        try:
            requirements = JobRequirements.model_validate(
                json.loads(job_requirements_json)
            )
        except (json.JSONDecodeError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail=(
                    "job_requirements_json is not valid "
                    "JobRequirements JSON."
                ),
            ) from exc

    elif job_description_text is not None:
        if not job_description_text.strip():
            raise HTTPException(
                status_code=400,
                detail="job_description_text cannot be empty.",
            )

        requirements = extraction.extract_job_requirements(
            job_description_text
        )

    else:
        assert job_description is not None

        if not (job_description.filename or "").lower().endswith(".txt"):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Job description uploads must currently "
                    "be TXT files."
                ),
            )

        content = await job_description.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded job description is empty.",
            )

        try:
            job_text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail="The job description must be valid UTF-8 text.",
            ) from exc

        requirements = extraction.extract_job_requirements(
            job_text
        )

    return build_resume_analysis(
        profile,
        requirements,
    )