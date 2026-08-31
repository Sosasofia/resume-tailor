from app.models import JobRequirements
from app.profile import ResumeProfile


SKILL_ALIASES: dict[str, str] = {
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "postgres db": "postgresql",
    "c sharp": "c#",
    "c#": "c#",
    "dotnet": ".net",
    ".net": ".net",
    "rest api": "rest apis",
    "rest apis": "rest apis",
    "restful api": "rest apis",
    "restful apis": "rest apis",
}


def normalize_skill(skill: str) -> str:
    normalized = " ".join(skill.lower().split())

    return SKILL_ALIASES.get(
        normalized,
        normalized,
    )


def match_skills(
    profile: ResumeProfile,
    requirements: JobRequirements,
) -> tuple[set[str], set[str]]:
    profile_skills = {
        normalize_skill(skill)
        for skill in profile.skills
    }

    required_skills = {
        normalize_skill(skill)
        for skill in requirements.required_skills
    }

    matching = profile_skills & required_skills
    missing = required_skills - profile_skills

    return matching, missing