from app.domain.models import ATSResume
from app.domain.profile import ResumeProfile


def render_markdown(
    profile: ResumeProfile,
    resume: ATSResume,
) -> str:
    lines: list[str] = []

    lines.append(f"# {profile.basics.name}")
    lines.append("")

    contact = [
        profile.basics.location,
        profile.basics.email,
    ]

    if profile.basics.linkedin:
        contact.append(profile.basics.linkedin)

    if profile.basics.github:
        contact.append(profile.basics.github)

    lines.append(" | ".join(contact))
    lines.append("")

    if resume.summary:
        lines.extend(
            [
                "## Summary",
                "",
                resume.summary,
                "",
            ]
        )

    if resume.skills:
        lines.extend(
            [
                "## Skills",
                "",
                *[f"- {skill}" for skill in resume.skills],
                "",
            ]
        )

    if resume.experience:
        lines.extend(
            [
                "## Experience",
                "",
                *[f"- {item}" for item in resume.experience],
                "",
            ]
        )

    if resume.projects:
        lines.extend(
            [
                "## Projects",
                "",
                *[f"- {item}" for item in resume.projects],
                "",
            ]
        )

    if resume.education:
        lines.extend(
            [
                "## Education",
                "",
                *[f"- {item}" for item in resume.education],
                "",
            ]
        )

    return "\n".join(lines)