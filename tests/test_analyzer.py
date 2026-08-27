from app.analyzer import compare_skills, find_skills


def test_compare_skills() -> None:
    resume = "Python, Docker and PostgreSQL"
    job_description = "Python, Docker, PostgreSQL and React"

    matching, missing = compare_skills(
        resume,
        job_description,
    )

    assert matching == {"python", "docker", "postgresql"}
    assert missing == {"react"}


def test_postgresql_does_not_match_sql() -> None:
    skills = find_skills("PostgreSQL")

    assert "postgresql" in skills
    assert "sql" not in skills


def test_skill_matching_is_case_insensitive() -> None:
    skills = find_skills("PYTHON, Docker, POSTGRESQL")

    assert skills == {"python", "docker", "postgresql"}


def test_missing_skill_is_detected() -> None:
    matching, missing = compare_skills(
        "Python and Docker",
        "Python, Docker and React",
    )

    assert matching == {"python", "docker"}
    assert missing == {"react"}
