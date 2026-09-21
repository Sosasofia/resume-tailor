import json
import tempfile
from pathlib import Path

from app.domain.models import JobRequirements
from app.domain.profile import ResumeProfile
from app.documents.parser import extract_pdf_text
from app.services import extraction


class InputValidationError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


def resolve_profile(
    profile_json: str | None,
    resume_filename: str | None,
    resume_content: bytes | None,
) -> ResumeProfile:
    sources = sum(
        source is not None
        for source in (
            profile_json,
            resume_content,
        )
    )

    if sources != 1:
        raise InputValidationError(
            "Exactly one resume source is required: "
            "'resume' or 'profile_json'."
        )

    if profile_json is not None:
        try:
            return ResumeProfile.model_validate(
                json.loads(profile_json)
            )
        except (json.JSONDecodeError, ValueError) as exc:
            raise InputValidationError(
                "profile_json is not valid ResumeProfile JSON."
            ) from exc

    filename = resume_filename or ""

    if Path(filename).suffix.lower() != ".pdf":
        raise InputValidationError(
            "Resume uploads must currently be PDF files."
        )

    if not resume_content:
        raise InputValidationError(
            "The uploaded resume is empty."
        )

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False,
    ) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        temp_path.write_bytes(resume_content)

        resume_text = extract_pdf_text(temp_path)

        return extraction.extract_resume_profile(
            resume_text
        )
    finally:
        temp_path.unlink(missing_ok=True)


def resolve_job_requirements(
    job_description_filename: str | None,
    job_description_content: bytes | None,
    job_description_text: str | None,
    job_requirements_json: str | None,
) -> JobRequirements:
    sources = sum(
        source is not None
        for source in (
            job_description_content,
            job_description_text,
            job_requirements_json,
        )
    )

    if sources != 1:
        raise InputValidationError(
            "Exactly one job source is required: "
            "'job_description', 'job_description_text', "
            "or 'job_requirements_json'."
        )

    if job_requirements_json is not None:
        try:
            return JobRequirements.model_validate(
                json.loads(job_requirements_json)
            )
        except (json.JSONDecodeError, ValueError) as exc:
            raise InputValidationError(
                "job_requirements_json is not valid "
                "JobRequirements JSON."
            ) from exc

    if job_description_text is not None:
        if not job_description_text.strip():
            raise InputValidationError(
                "job_description_text cannot be empty."
            )

        return extraction.extract_job_requirements(
            job_description_text
        )

    filename = job_description_filename or ""

    if Path(filename).suffix.lower() != ".txt":
        raise InputValidationError(
            "Job description uploads must currently be "
            "TXT files."
        )

    if not job_description_content:
        raise InputValidationError(
            "The uploaded job description is empty."
        )

    try:
        job_text = job_description_content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InputValidationError(
            "The job description must be valid UTF-8 text."
        ) from exc

    return extraction.extract_job_requirements(
        job_text
    )