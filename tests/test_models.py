import pytest 
from pydantic import ValidationError

from app.models import JobAnalysis


def test_job_analysis_accepts_valid_data() -> None:
    analysis = JobAnalysis(
        match_score=0.78,
        matching_skills=["Python", "Docker"],
        missing_skills=["React"],
        matching_experience=["Backend development"],
        recommendations=["Highlight API experience"],
    )

    assert analysis.match_score == 0.78
    assert "Python" in analysis.matching_skills


def test_match_score_must_be_between_zero_and_one() -> None:
    with pytest.raises(ValidationError):
        JobAnalysis(
            match_score=1.5,
            matching_skills=[],
            missing_skills=[],
            matching_experience=[],
            recommendations=[],
        )
