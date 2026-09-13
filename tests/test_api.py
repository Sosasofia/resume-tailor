import json


from fastapi.testclient import TestClient


from app.api.main import app
from app.models import ATSResume, JobRequirements, ResumeStrategy
from app.profile import (
    Basics,
    Education,
    ResumeProfile,
)
from app.api import routes


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_rejects_empty_file() -> None:
    response = client.post(
        "/extract",
        files={
            "document": (
                "resume.pdf",
                b"",
                "application/pdf",
            )
        },
        data={
            "document_type": "resume",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded document is empty."

def build_profile() -> ResumeProfile:
    return ResumeProfile(
        basics=Basics(
            name="Test User",
            location="Buenos Aires",
            email="test@example.com",
        ),
        summary="Backend developer.",
        skills=["Python", "Docker", "SQL"],
        experience=[],
        projects=[],
        education=[
            Education(
                institution="Test University",
                location="Argentina",
                degree="Software Engineering",
                start_year=2020,
                end_year=2024,
            )
        ],
    )


def build_requirements() -> JobRequirements:
    return JobRequirements(
        required_skills=["Python", "Docker"],
        preferred_skills=["Azure"],
        responsibilities=["Develop backend services"],
        keywords=["backend", "Python"],
    )


def build_resume() -> ATSResume:
    return ATSResume(
        summary="Backend developer with Python experience.",
        skills=["Python", "Docker"],
        experience=["Developed backend services."],
        projects=[],
        education=["Software Engineering"],
    )

def test_tailor_with_profile_json_and_job_text(
    monkeypatch,
) -> None:
    profile = build_profile()
    requirements = build_requirements()
    resume = build_resume()

    monkeypatch.setattr(
        routes,
        "extract_job_requirements",
        lambda _: requirements,
    )

    monkeypatch.setattr(
        routes,
        "generate_ats_resume",
        lambda profile, requirements, strategy: resume,
    )

    response = client.post(
        "/tailor",
        data={
            "format": "markdown",
            "profile_json": profile.model_dump_json(),
            "job_description_text": "Python backend developer",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "text/markdown"
    )
    assert (
        'attachment; filename="tailored_resume.md"'
        in response.headers["content-disposition"]
    )
    assert "# Test User" in response.text
    assert "Python" in response.text


def test_tailor_requires_one_resume_source() -> None:
    response = client.post(
        "/tailor",
        data={
            "format": "markdown",
            "job_description_text": "Python backend developer",
        },
    )

    assert response.status_code == 400
    assert "Exactly one resume source" in response.json()["detail"]

def test_tailor_rejects_multiple_resume_sources() -> None:
    profile = build_profile()

    response = client.post(
        "/tailor",
        data={
            "format": "markdown",
            "profile_json": profile.model_dump_json(),
            "job_description_text": "Python backend developer",
        },
        files={
            "resume": (
                "resume.pdf",
                b"fake pdf",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert "Exactly one resume source" in response.json()["detail"]

def test_tailor_requires_one_job_source() -> None:
    profile = build_profile()

    response = client.post(
        "/tailor",
        data={
            "format": "markdown",
            "profile_json": profile.model_dump_json(),
        },
    )

    assert response.status_code == 400
    assert "Exactly one job source" in response.json()["detail"]

def test_tailor_rejects_multiple_job_sources() -> None:
    profile = build_profile()

    requirements = build_requirements()

    response = client.post(
        "/tailor",
        data={
            "format": "markdown",
            "profile_json": profile.model_dump_json(),
            "job_description_text": "Python backend developer",
            "job_requirements_json": requirements.model_dump_json(),
        },
    )

    assert response.status_code == 400
    assert "Exactly one job source" in response.json()["detail"]

def test_tailor_rejects_invalid_profile_json() -> None:
    response = client.post(
        "/tailor",
        data={
            "format": "markdown",
            "profile_json": "{not valid json}",
            "job_description_text": "Python backend developer",
        },
    )

    assert response.status_code == 400
    assert "profile_json" in response.json()["detail"]


def test_tailor_accepts_job_requirements_json(
    monkeypatch,
) -> None:
    profile = build_profile()
    requirements = build_requirements()
    resume = build_resume()

    monkeypatch.setattr(
        routes,
        "generate_ats_resume",
        lambda profile, requirements, strategy: resume,
    )

    response = client.post(
        "/tailor",
        data={
            "format": "markdown",
            "profile_json": profile.model_dump_json(),
            "job_requirements_json": requirements.model_dump_json(),
        },
    )

    assert response.status_code == 200
    assert "# Test User" in response.text

