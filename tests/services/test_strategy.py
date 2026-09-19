from app.domain.models import JobRequirements
from app.domain.profile import Basics, Education, ResumeProfile
from app.services.matching import build_resume_strategy


def test_build_resume_strategy() -> None:
    profile = ResumeProfile(
        basics=Basics(
            name="Test User",
            location="Buenos Aires",
            email="test@example.com",
        ),
        summary="Backend developer with API experience.",
        skills=[
            "C#",
            ".NET",
            "Docker",
        ],
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

    requirements = JobRequirements(
        required_skills=[
            ".NET",
            "C#",
            "PostgreSQL",
            "Docker",
        ],
        preferred_skills=["Azure"],
        responsibilities=[
            "Develop backend services",
        ],
        keywords=[
            ".NET",
            "Docker",
            "backend",
        ],
    )

    strategy = build_resume_strategy(
        profile,
        requirements,
    )

    assert set(strategy.matching_skills) == {
        ".net",
        "c#",
        "docker",
    }

    assert strategy.missing_required_skills == [
        "postgresql"
    ]

    assert strategy.relevant_projects == []