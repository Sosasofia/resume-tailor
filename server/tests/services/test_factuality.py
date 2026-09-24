from app.services import validation
from app.domain.models import (
    ATSResume,
    FactualityIssue,
    FactualityResult,
)
from tests.helpers import make_profile, FakeClient


def test_supported_resume_is_approved(monkeypatch):
    expected = FactualityResult(
        approved=True,
        issues=[],
    )

    monkeypatch.setattr(
        "app.clients.azure_openai.create_client",
        lambda: FakeClient(expected),
    )

    resume = ATSResume(
        summary="Backend developer",
        skills=["Python", "SQL", "Docker"],
        experience=[
            "Designed and implemented a microservices architecture."
        ],
        projects=[],
        education=[],
    )

    result = validation.validate_factuality(
        make_profile(),
        resume,
    )

    assert result.approved is True
    assert result.issues == []


def test_unsupported_claim_is_rejected(monkeypatch):
    expected = FactualityResult(
        approved=False,
        issues=[
            FactualityIssue(
                section="skills",
                claim="Kubernetes",
                reason="Kubernetes is not present in the candidate profile.",
            )
        ],
    )

    monkeypatch.setattr(
        "app.clients.azure_openai.create_client",
        lambda: FakeClient(expected),
    )

    resume = ATSResume(
        summary="Backend developer",
        skills=["Python", "Kubernetes"],
        experience=[],
        projects=[],
        education=[],
    )

    result = validation.validate_factuality(
        make_profile(),
        resume,
    )

    assert result.approved is False
    assert len(result.issues) == 1
    assert result.issues[0].claim == "Kubernetes"