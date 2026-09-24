from app.domain.models import ATSResume
from app.domain.profile import (
    Basics,
    Education,
    Experience,
    Project,
    ResumeProfile,
)
from app.services import validation


def make_profile() -> ResumeProfile:
    return ResumeProfile(
        basics=Basics(
            name="Victor Vigon",
            location="Buenos Aires, Argentina",
            email="victor@example.com",
        ),
        summary="Backend developer",
        skills=[
            "Python",
            "SQL",
            "Docker",
        ],
        experience=[
            Experience(
                company="Nutbank",
                role="Back End Developer",
                location="Argentina",
                start_year=2020,
                end_year=2024,
                achievements=[
                    "Designed microservices architecture",
                ],
            )
        ],
        projects=[
            Project(
                name="MercadoCat",
                year=2024,
                description="E-commerce project",
            )
        ],
        education=[
            Education(
                institution="University of Buenos Aires",
                location="Buenos Aires",
                degree="Computer Science",
                start_year=2015,
                end_year=2020,
            )
        ],
    )


def test_supported_skills_are_approved():
    profile = make_profile()

    resume = ATSResume(
        summary="Backend developer",
        skills=["Python", "SQL", "Docker"],
        experience=["Back End Developer at Nutbank"],
        projects=["MercadoCat"],
        education=["Computer Science - University of Buenos Aires"],
    )

    result = validation.validate_resume(profile, resume)

    assert result.approved is True
    assert result.errors == []


def test_unsupported_skill_is_rejected():
    profile = make_profile()

    resume = ATSResume(
        summary="Backend developer",
        skills=["Python", "Kubernetes"],
        experience=[],
        projects=[],
        education=[],
    )

    result = validation.validate_resume(profile, resume)

    assert result.approved is False
    assert "Unsupported skill: Kubernetes" in result.errors


def test_unsupported_education_is_rejected():
    profile = make_profile()

    resume = ATSResume(
        summary="Backend developer",
        skills=[],
        experience=[],
        projects=[],
        education=["MIT - Computer Science"],
    )

    result = validation.validate_resume(profile, resume)

    assert result.approved is False
    assert any(
        "MIT" in error
        for error in result.errors
    )