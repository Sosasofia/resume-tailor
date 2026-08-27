from app.analyzer import compare_skills


def test_compare_skills() -> None:
    resume = "Python, Docker and PostgreSQL"
    job_description = "Python, Docker, PostgreSQL and React"

    matching, missing = compare_skills(
        resume,
        job_description,
    )

    assert matching == {"python", "docker", "postgresql"}
    assert missing == {"react"}
