from fastapi.testclient import TestClient


from app.main import app
from app.domain.models import ATSResume, FactualityResult, JobRequirements
from app.domain.profile import (
    Basics,
    Education,
    ResumeProfile,
)
from tests.helpers import make_profile


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
            "app.services.extraction.extract_job_requirements",
            lambda _: requirements,
        )

        monkeypatch.setattr(
            "app.services.tailoring.generate_validated_resume",
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
            "app.services.tailoring.generate_validated_resume",
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


def test_tailor_rejects_unsupported_resume_claim(client, monkeypatch):
    invalid_resume = ATSResume(
        summary="Backend developer",
        skills=["Python", "Kubernetes"],
        experience=[],
        projects=[],
        education=[],
    )

    monkeypatch.setattr(
        "app.services.tailoring.generate_ats_resume",
        lambda profile, requirements, strategy: invalid_resume,
    )

    response = client.post(
        "/tailor",
        data={
            "format": "markdown",
            "profile_json": make_profile().model_dump_json(),
            "job_description_text": "Looking for a Python backend developer.",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["detail"]["stage"] == "deterministic_factuality"
    assert any(
        "Kubernetes" in error
        for error in body["detail"]["errors"]
    )


def test_tailor_does_not_render_invalid_resume(client, monkeypatch):
    invalid_resume = ATSResume(
        summary="Backend developer",
        skills=["Kubernetes"],
        experience=[],
        projects=[],
        education=[],
    )

    monkeypatch.setattr(
        "app.services.tailoring.generate_ats_resume",
        lambda profile, requirements, strategy: invalid_resume,
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Renderer should not be called")

    monkeypatch.setattr(
        "app.documents.markdown.render_markdown",
        fail_if_called,
    )

    response = client.post(
        "/tailor",
        data={
            "format": "markdown",
            "profile_json": make_profile().model_dump_json(),
            "job_description_text": "Python backend developer",
        },
    )

    assert response.status_code == 422


def test_tailor_renders_valid_resume(client, monkeypatch):
    valid_resume = ATSResume(
        summary="Backend developer",
        skills=["Python"],
        experience=[],
        projects=[],
        education=[],
    )

    monkeypatch.setattr(
        "app.services.tailoring.generate_ats_resume",
        lambda profile, requirements, strategy: valid_resume,
    )

    monkeypatch.setattr(
        "app.services.validation.validate_factuality",
        lambda profile, resume: FactualityResult(
            approved=True,
            issues=[],
        ),
    )

