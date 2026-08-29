from app.models import ResumeChange
from app.validator import validate_change


def test_valid_change_is_approved() -> None:
    resume = """
    Developed backend applications using C# and .NET.
    Built REST APIs for internal applications.
    """

    change = ResumeChange(
        section="Experience",
        original="Developed backend applications using C# and .NET.",
        suggested=(
            "Developed backend applications using C# and .NET "
            "to build REST APIs."
        ),
        reason="Better alignment with the job description.",
    )

    result = validate_change(change, resume)

    assert result.approved is True


def test_change_with_unsupported_skill_is_rejected() -> None:
    resume = """
    Developed backend applications using C# and .NET.
    """

    change = ResumeChange(
        section="Experience",
        original="Developed backend applications using C# and .NET.",
        suggested=(
            "Developed backend applications using C# and .NET "
            "with Kubernetes."
        ),
        reason="Aligns with the job description.",
    )

    result = validate_change(change, resume)

    assert result.approved is False
    assert "kubernetes" in result.reason


def test_change_is_rejected_when_original_text_is_missing() -> None:
    resume = """
    Developed backend applications using C# and .NET.
    """

    change = ResumeChange(
        section="Experience",
        original="Worked with Java and Spring.",
        suggested="Worked with Java and Spring Boot.",
        reason="Improved alignment.",
    )

    result = validate_change(change, resume)

    assert result.approved is False
    assert "original text was not found" in result.reason


def test_fabricated_percentage_is_rejected() -> None:
    resume = """
    Developed REST APIs using C# and .NET.
    """

    change = ResumeChange(
        section="Experience",
        original="Developed REST APIs using C# and .NET.",
        suggested=(
            "Developed REST APIs using C# and .NET, "
            "reducing response time by 40%."
        ),
        reason="Stronger achievement statement.",
    )

    result = validate_change(change, resume)

    assert result.approved is False
    assert "40" in result.reason


def test_number_already_supported_by_resume_is_allowed() -> None:
    resume = """
    Developed 5 REST APIs using C# and .NET.
    """

    change = ResumeChange(
        section="Experience",
        original="Developed 5 REST APIs using C# and .NET.",
        suggested=(
            "Developed 5 REST APIs using C# and .NET "
            "for internal applications."
        ),
        reason="Adds context.",
    )

    result = validate_change(change, resume)

    assert result.approved is True


def test_fabricated_year_is_rejected() -> None:
    resume = """
    Software Developer at Example Corp.
    """

    change = ResumeChange(
        section="Experience",
        original="Software Developer at Example Corp.",
        suggested=(
            "Software Developer at Example Corp. "
            "from 2022."
        ),
        reason="Adds employment date.",
    )

    result = validate_change(change, resume)

    assert result.approved is False
    assert "2022" in result.reason