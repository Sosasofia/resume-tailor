from pathlib import Path
from typing import Literal


from fastapi import APIRouter, File, Form, UploadFile, HTTPException


from app.api.schemas import AnalyzeRequest, AnalyzeResponse, ExtractResponse
from app.llm import extract_resume_profile, extract_job_requirements
from app.matcher import match_skills
from app.parser import extract_pdf_text
from app.profile_loader import load_profile


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