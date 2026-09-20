import json
import tempfile
from pathlib import Path
from typing import Literal


from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Response, BackgroundTasks
from fastapi.responses import FileResponse


from app.services import (
    tailoring,
    extraction
)
from app.api.schemas import TailorValidationErrorResponse
from app.domain.profile import ResumeProfile
from app.domain.models import JobRequirements
from app.services.matching import build_resume_strategy
from app.documents.markdown import render_markdown
from app.documents.parser import extract_pdf_text
from app.documents.pdf import create_pdf


router = APIRouter(
    prefix="",
    tags=["tailor"],
)


@router.post("/tailor")
async def tailor(
    background_tasks: BackgroundTasks,
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

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            temp_path.write_bytes(content)

            resume_text = extract_pdf_text(temp_path)
            profile = extraction.extract_resume_profile(
                resume_text
            )
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

        requirements = extraction.extract_job_requirements(
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

        requirements = extraction.extract_job_requirements(
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
    try:
        ats_resume = tailoring.generate_validated_resume(
            profile,
            requirements,
            strategy,
        )
    except tailoring.TailoringValidationError as exc:
        error_response = TailorValidationErrorResponse(
            stage=exc.stage,
            errors=exc.errors,
            issues=exc.issues,
        )

        raise HTTPException(
            status_code=422,
            detail=error_response.model_dump(),
        ) from exc

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

    if format == "pdf":
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        )

        output_path = Path(temp_file.name)
        temp_file.close()

        create_pdf(
            profile,
            ats_resume,
            output_path,
        )

        background_tasks.add_task(
            output_path.unlink,
            missing_ok=True,
        )

        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename="tailored_resume.pdf",
        )
