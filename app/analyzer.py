import re
from typing import Final


SKILLS: Final[set[str]] = {
    "python",
    "c#",
    ".net",
    "react",
    "sql",
    "postgresql",
    "docker",
    "azure",
    "rest",
    "rest api",
    "javascript",
    "typescript",
}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def find_skills(text: str) -> set[str]:
    normalized_text = normalize(text)
    found_skills: set[str] = set()

    for skill in SKILLS:
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

        if re.search(pattern, normalized_text):
            found_skills.add(skill)

    return found_skills


def compare_skills(
    resume_text: str,
    job_description: str,
) -> tuple[set[str], set[str]]:
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_description)

    matching_skills = resume_skills & job_skills
    missing_skills = job_skills - resume_skills

    return matching_skills, missing_skills
