import tempfile
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Response, BackgroundTasks
from fastapi.responses import FileResponse

from app.services import (
    tailoring,
)
from app.services.input import (
    InputValidationError,
    resolve_job_requirements,
    resolve_profile,
)
from app.api.schemas import TailorValidationErrorResponse
from app.documents.markdown import render_markdown
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

    # ---------------------------------------------------------
    # Resume
    # ---------------------------------------------------------
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


    # ---------------------------------------------------------
    # Generate ATS resume
    # ---------------------------------------------------------
    try:
        ats_resume = tailoring.tailor_resume(
            profile,
            requirements,
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
