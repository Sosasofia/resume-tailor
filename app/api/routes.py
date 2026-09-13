import json
from pathlib import Path
from typing import Literal


from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Response


from app.api.schemas import AnalyzeRequest, AnalyzeResponse, ExtractResponse, ExtractResponse
from app.llm import (
    extract_job_requirements,
    extract_resume_profile,
    generate_ats_resume,
)
from app.profile import ResumeProfile
from app.models import JobRequirements
from app.markdown import render_markdown
from app.matcher import match_skills
from app.parser import extract_pdf_text
from app.profile_loader import load_profile
from app.strategy import build_resume_strategy


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/extract")
async def extract(
    document: UploadFile = File(...),
    document_type: Literal["resume", "job_description"] = Form(...),
) -> ExtractResponse:
    content = await document.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded document is empty.",
        )

    suffix = Path(document.filename or "").suffix.lower()

    if suffix != ".pdf" and document_type == "resume":
        raise HTTPException(
            status_code=400,
            detail="Resume extraction currently supports PDF files.",
        )

    if suffix != ".txt" and document_type == "job_description":
        raise HTTPException(
            status_code=400,
            detail="Job description extraction currently supports TXT files.",
        )

    temp_dir = Path("/tmp/resume-tailor")
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp_path = temp_dir / (document.filename or "document")

    temp_path.write_bytes(content)

    try:
        if document_type == "resume":
            resume_text = extract_pdf_text(temp_path)
            data = extract_resume_profile(resume_text)

        else:
            job_description = temp_path.read_text(
                encoding="utf-8"
            )
            data = extract_job_requirements(job_description)

    finally:
        temp_path.unlink(missing_ok=True)

    return ExtractResponse(
        document_type=document_type,
        data=data,
    ).model_dump()


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


@router.post("/tailor")
async def tailor(
    format: Literal["markdown", "pdf"] = Form(...),

    resume: UploadFile | None = File(None),
    profile_json: str | None = Form(None),

    job_description: UploadFile | None = File(None),
    job_description_text: str | None = Form(None),
    job_requirements_json: str | None = Form(None),
):
    # ---------------------------------------------------------
    # Validate resume source
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Validate job source
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Resume
    # ---------------------------------------------------------
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

        filename = resume.filename or ""
        if Path(filename).suffix.lower() != ".pdf":
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

        temp_path = Path("/tmp/resume-tailor-resume.pdf")

        try:
            temp_path.write_bytes(content)
            resume_text = extract_pdf_text(temp_path)
            profile = extract_resume_profile(resume_text)
        finally:
            temp_path.unlink(missing_ok=True)

    # ---------------------------------------------------------
    # Job requirements
    # ---------------------------------------------------------
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

        requirements = extract_job_requirements(
            job_description_text
        )

    else:
        assert job_description is not None

        filename = job_description.filename or ""
        if Path(filename).suffix.lower() != ".txt":
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

        job_text = content.decode("utf-8")

        requirements = extract_job_requirements(
            job_text
        )

    # ---------------------------------------------------------
    # Strategy
    # ---------------------------------------------------------
    strategy = build_resume_strategy(
        profile,
        requirements,
    )

    # ---------------------------------------------------------
    # Generate ATS resume
    # ---------------------------------------------------------
    ats_resume = generate_ats_resume(
        profile,
        requirements,
        strategy,
    )

    # ---------------------------------------------------------
    # Format
    # ---------------------------------------------------------
    if format == "markdown":
        markdown = render_markdown(
            profile,
            ats_resume,
        )

        return Response(
            content=markdown,
            media_type="text/markdown",
            headers={
                "Content-Disposition": (
                    'attachment; filename="tailored_resume.md"'
                )
            },
        )

    raise HTTPException(
        status_code=501,
        detail="PDF output is not implemented on this endpoint yet.",
    )