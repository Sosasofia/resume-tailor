from app.domain.models import (
    ATSResume,
    FactualityResult,
    JobRequirements,
    ResumeStrategy,
)
from app.domain.profile import (
    Basics,
    ResumeProfile,
)
from app.services import (
    tailoring
)
from app.services.tailoring import TailoringValidationError, tailor_resume


def make_profile() -> ResumeProfile:
    return ResumeProfile(
        basics=Basics(
            name="Victor Vigon",
            location="Buenos Aires",
            email="victor@example.com",
        ),
        summary="Backend developer",
        skills=["Python", "SQL", "Docker"],
        experience=[],
        projects=[],
        education=[],
    )


def make_requirements() -> JobRequirements:
    return JobRequirements(
        required_skills=["Python"],
        preferred_skills=[],
        responsibilities=[],
        keywords=["backend"],
    )


def make_strategy() -> ResumeStrategy:
    return ResumeStrategy(
        priority_skills=["Python"],
        matching_skills=["Python"],
        missing_required_skills=[],
        relevant_experience=[],
        relevant_projects=[],
        keywords_to_use=["backend"],
    )


def make_resume() -> ATSResume:
    return ATSResume(
        summary="Backend developer with Python experience.",
        skills=["Python"],
        experience=[],
        projects=[],
        education=[],
    )


def test_generated_resume_is_rejected_when_deterministic_validation_fails(
    monkeypatch,
):
    resume = ATSResume(
        summary="Backend developer",
        skills=["Python", "Kubernetes"],
        experience=[],
        projects=[],
        education=[],
    )

    monkeypatch.setattr(
        "app.services.tailoring.generate_ats_resume",
        lambda profile, requirements, strategy, **kwargs: resume,
    )

    try:
        tailoring.generate_validated_resume(
            make_profile(),
            make_requirements(),
            make_strategy(),
        )
        assert False, "Expected validation error"
    except TailoringValidationError as exc:
        assert exc.stage == "deterministic_factuality"
        assert any(
            "Kubernetes" in error
            for error in exc.errors
        )


def test_generated_resume_passes_both_validation_layers(
    monkeypatch,
):
    resume = ATSResume(
        summary="Backend developer",
        skills=["Python"],
        experience=[],
        projects=[],
        education=[],
    )

    monkeypatch.setattr(
        "app.services.tailoring.generate_ats_resume",
        lambda profile, requirements, strategy, **kwargs: resume,
    )

    monkeypatch.setattr(
        "app.services.validation.validate_factuality",
        lambda profile, resume: FactualityResult(
            approved=True,
            issues=[],
        ),
    )

    result = tailoring.generate_validated_resume(
        make_profile(),
        make_requirements(),
        make_strategy(),
    )

    assert result == resume


def test_tailor_resume_builds_strategy_and_generates_validated_resume(
    monkeypatch,
):
    profile = make_profile()
    requirements = make_requirements()
    resume = make_resume()

    monkeypatch.setattr(
        "app.services.tailoring.build_resume_strategy",
        lambda profile, requirements: make_strategy(),
    )

    monkeypatch.setattr(
        "app.services.tailoring.generate_validated_resume",
        lambda profile, requirements, strategy: resume,
    )

    result = tailor_resume(
        profile,
        requirements,
    )

    assert result == resume