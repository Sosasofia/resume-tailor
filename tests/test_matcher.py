from app.matcher import match_skills, normalize_skill
from app.models import JobRequirements
from app.profile import (
    Basics,
    Education,
    ResumeProfile,
)


def test_match_required_skills() -> None:
    profile = ResumeProfile(
        basics=Basics(
            name="Test User",
            location="Buenos Aires",
            email="test@example.com",
        ),
        summary="Backend developer",
        skills=["C#", ".NET", "Docker"],
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
            "C#",
            ".NET",
            "PostgreSQL",
            "Docker",
        ],
        preferred_skills=[],
        responsibilities=[],
        keywords=[],
    )

    matching, missing = match_skills(
        profile,
        requirements,
    )

    assert matching == {"c#", ".net", "docker"}
    assert missing == {"postgresql"}

def test_skill_aliases_are_normalized() -> None:
    assert normalize_skill("Postgres") == "postgresql"
    assert normalize_skill("C Sharp") == "c#"
    assert normalize_skill("dotnet") == ".net"
    assert normalize_skill("RESTful APIs") == "rest apis"


def test_unknown_skill_is_normalized_without_alias() -> None:
    assert normalize_skill("  Kafka  ") == "kafka"