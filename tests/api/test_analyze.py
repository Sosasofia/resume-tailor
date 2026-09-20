from fastapi.testclient import TestClient

from app.main import app
from tests.api.test_api import build_profile, build_requirements


client = TestClient(app)


def test_analyze_with_profile_json_and_job_requirements():
    profile = build_profile()
    requirements = build_requirements()

    response = client.post(
        "/analyze",
        data={
            "profile_json": profile.model_dump_json(),
            "job_requirements_json": requirements.model_dump_json(),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "match_score" in body
    assert "matching_skills" in body
    assert "missing_required_skills" in body
    assert "relevant_experience" in body
    assert "relevant_projects" in body
    assert "recommendations" in body


def test_analyze_requires_one_resume_source():
    response = client.post(
        "/analyze",
        data={
            "job_requirements_json": (
                build_requirements().model_dump_json()
            ),
        },
    )

    assert response.status_code == 400


def test_analyze_requires_one_job_source():
    response = client.post(
        "/analyze",
        data={
            "profile_json": build_profile().model_dump_json(),
        },
    )

    assert response.status_code == 400