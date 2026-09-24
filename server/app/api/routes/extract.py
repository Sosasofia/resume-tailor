from pathlib import Path
from typing import Literal


from fastapi import APIRouter, File, Form, UploadFile, HTTPException


from app.api.schemas import (
    ExtractResponse, ExtractResponse
)
from app.services.extraction import (
    extract_job_requirements,
    extract_resume_profile
)
from app.documents.parser import extract_pdf_text


router = APIRouter(
    prefix="",
    tags=["extract"],
)


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
