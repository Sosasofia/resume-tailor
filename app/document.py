from pathlib import Path

import typst

from app.models import ATSResume, JobRequirements, ResumeStrategy
from app.profile import ResumeProfile


def escape_typst(text: str) -> str:
    """Escapes special Typst characters to prevent compilation errors."""
    if not text:
        return ""

    escaped_text = text
    for char in ["#", "$", "<", ">", "@", "*", "_", "`"]:
        escaped_text = escaped_text.replace(char, f"\\{char}")
    return escaped_text


def create_ats_document(
    profile: ResumeProfile,
    resume: ATSResume,
    output_path: Path,
    output_format: str = "pdf",
    requirements: JobRequirements | None = None,
    strategy: ResumeStrategy | None = None,
) -> Path:
    if output_format not in {"pdf", "markdown"}:
        raise ValueError(f"Unsupported output format: {output_format}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "markdown":
        markdown_path = output_path.with_suffix(".md")
        markdown_path.write_text(
            _build_markdown(profile, resume, requirements, strategy),
            encoding="utf-8",
        )
        return markdown_path

    contact_info = [
        escape_typst(profile.basics.location),
        escape_typst(profile.basics.email),
    ]
    if profile.basics.linkedin:
        contact_info.append(escape_typst(profile.basics.linkedin))
    if profile.basics.github:
        contact_info.append(escape_typst(profile.basics.github))

    typst_content = f"""
#set page(margin: (x: 1in, y: 1in))
#set text(font: "Arial", size: 10pt)
#set par(justify: true)

#align(center)[
  = {escape_typst(profile.basics.name)}
  {" | ".join(contact_info)}
]

== Summary
{escape_typst(resume.summary)}

== Skills
"""
    for skill in resume.skills:
        typst_content += f"- {escape_typst(skill)}\n"
    typst_content += "\n== Experience\n"
    for experience in resume.experience:
        typst_content += f"- {escape_typst(experience)}\n"
    typst_content += "\n== Projects\n"
    for project in resume.projects:
        typst_content += f"- {escape_typst(project)}\n"
    typst_content += "\n== Education\n"
    for education in resume.education:
        typst_content += f"- {escape_typst(education)}\n"

    typst_path = output_path.with_suffix(".typ")
    typst_path.write_text(typst_content, encoding="utf-8")
    pdf_path = output_path.with_suffix(".pdf")
    typst.compile(str(typst_path), output=str(pdf_path))
    return pdf_path


def _build_markdown(
    profile: ResumeProfile,
    resume: ATSResume,
    requirements: JobRequirements | None,
    strategy: ResumeStrategy | None,
) -> str:
    lines = [f"# {profile.basics.name}", "", profile.basics.location, profile.basics.email]
    if profile.basics.linkedin:
        lines.append(profile.basics.linkedin)
    if profile.basics.github:
        lines.append(profile.basics.github)

    lines.extend(["", "## Summary", "", resume.summary, "", "## Skills", ""])
    lines.extend(f"- {skill}" for skill in resume.skills)
    lines.extend(["", "## Experience", ""])
    lines.extend(f"- {experience}" for experience in resume.experience)
    lines.extend(["", "## Projects", ""])
    lines.extend(f"- {project}" for project in resume.projects)
    lines.extend(["", "## Education", ""])
    lines.extend(f"- {education}" for education in resume.education)

    if requirements is not None:
        lines.extend(["", "## Job Requirements", "", "### Required Skills", ""])
        lines.extend(f"- {skill}" for skill in requirements.required_skills)
        lines.extend(["", "### Preferred Skills", ""])
        lines.extend(f"- {skill}" for skill in requirements.preferred_skills)
        lines.extend(["", "### Responsibilities", ""])
        lines.extend(f"- {item}" for item in requirements.responsibilities)
        lines.extend(["", "### Keywords", ""])
        lines.extend(f"- {keyword}" for keyword in requirements.keywords)

    if strategy is not None:
        lines.extend(["", "## Resume Strategy", "", "### Matching Skills", ""])
        lines.extend(f"- {skill}" for skill in strategy.matching_skills)
        lines.extend(["", "### Missing Required Skills", ""])
        lines.extend(f"- {skill}" for skill in strategy.missing_required_skills)
        lines.extend(["", "### Keywords To Use", ""])
        lines.extend(f"- {keyword}" for keyword in strategy.keywords_to_use)

    return "\n".join(lines) + "\n"
