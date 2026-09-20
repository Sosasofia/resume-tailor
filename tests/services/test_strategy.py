from app.domain.models import JobRequirements
from app.domain.profile import Basics, Education, ResumeProfile
from app.services.matching import build_resume_analysis, build_resume_strategy, calculate_match_score
from tests.services.test_tailor import make_profile, make_requirements


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


def test_calculate_match_score():
    assert calculate_match_score(
        {"python", "docker"},
        {"python", "docker", "sql"},
    ) == 67


def test_calculate_match_score_with_no_requirements():
    assert calculate_match_score(
        {"python"},
        set(),
    ) == 0


def test_build_resume_analysis():
    profile = make_profile()
    requirements = make_requirements()

    analysis = build_resume_analysis(
        profile,
        requirements,
    )

    assert analysis.match_score == 100
    assert analysis.matching_skills == [
        "python",
    ]
    assert analysis.missing_required_skills == []