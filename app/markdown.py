from app.models import ATSResume
from app.profile import ResumeProfile


def render_markdown(
    profile: ResumeProfile,
    resume: ATSResume,
) -> str:
    lines: list[str] = []

    lines.append(f"# {profile.basics.name}")
    lines.append("")

    contact = [profile.basics.location, profile.basics.email]

    if profile.basics.linkedin:
        contact.append(profile.basics.linkedin)

    if profile.basics.github:
        contact.append(profile.basics.github)

    lines.append(" | ".join(contact))
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(resume.summary)
    lines.append("")

    lines.append("## Skills")
    lines.append("")

    for skill in resume.skills:
        lines.append(f"- {skill}")

    lines.append("")

    lines.append("## Experience")
    lines.append("")

    for experience in resume.experience:
        lines.append(f"- {experience}")

    lines.append("")

    lines.append("## Projects")
    lines.append("")

    for project in resume.projects:
        lines.append(f"- {project}")

    lines.append("")

    lines.append("## Education")
    lines.append("")

    for education in resume.education:
        lines.append(f"- {education}")

    lines.append("")

    return "\n".join(lines)