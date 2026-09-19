from app.domain.models import JobRequirements, ResumeStrategy
from app.domain.profile import ResumeProfile


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


def build_resume_strategy(
    profile: ResumeProfile,
    requirements: JobRequirements,
) -> ResumeStrategy:
    matching_skills, missing_skills = match_skills(
        profile,
        requirements,
    )

    priority_skills = [
        skill
        for skill in requirements.required_skills
        if normalize_skill(skill) in matching_skills
    ]

    relevant_experience: list[str] = []

    for experience in profile.experience:
        experience_text = " ".join(
            [
                experience.role,
                experience.company,
                *experience.achievements,
            ]
        ).lower()

        for responsibility in requirements.responsibilities:
            responsibility_words = [
                word.lower()
                for word in responsibility.split()
                if len(word) > 3
            ]

            if any(
                word in experience_text
                for word in responsibility_words
            ):
                relevant_experience.append(
                    experience.company
                )
                break

    relevant_projects: list[str] = []

    for project in profile.projects:
        project_text = " ".join(
            [
                project.name,
                project.description,
                *project.achievements,
            ]
        ).lower()

        if any(
            keyword.lower() in project_text
            for keyword in requirements.keywords
        ):
            relevant_projects.append(project.name)

    keywords_to_use = [
        keyword
        for keyword in requirements.keywords
        if keyword.lower() in profile.summary.lower()
        or any(
            keyword.lower() in achievement.lower()
            for experience in profile.experience
            for achievement in experience.achievements
        )
    ]

    return ResumeStrategy(
        priority_skills=priority_skills,
        matching_skills=sorted(matching_skills),
        missing_required_skills=sorted(missing_skills),
        relevant_experience=sorted(set(relevant_experience)),
        relevant_projects=sorted(set(relevant_projects)),
        keywords_to_use=keywords_to_use,
    )