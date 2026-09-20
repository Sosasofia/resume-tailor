from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from app.domain.models import ATSResume
from app.domain.profile import ResumeProfile


def _safe_text(value: str) -> str:
    return escape(value)


def create_pdf(
    profile: ResumeProfile,
    resume: ATSResume,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "ResumeName",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    contact_style = ParagraphStyle(
        "ResumeContact",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        spaceAfter=10,
    )

    section_style = ParagraphStyle(
        "ResumeSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13,
        spaceAfter=3,
    )

    bullet_style = ParagraphStyle(
        "ResumeBullet",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
    )

    story = []

    story.append(
        Paragraph(
            _safe_text(profile.basics.name),
            name_style,
        )
    )

    contact = [
        profile.basics.location,
        profile.basics.email,
    ]

    if profile.basics.linkedin:
        contact.append(profile.basics.linkedin)

    if profile.basics.github:
        contact.append(profile.basics.github)

    story.append(
        Paragraph(
            _safe_text(" | ".join(contact)),
            contact_style,
        )
    )
    story.append(Spacer(1, 12))

    story.append(
        Paragraph("Summary", section_style)
    )

    story.append(
        Paragraph(
            _safe_text(resume.summary),
            body_style,
        )
    )

    story.append(
        Paragraph("Skills", section_style)
    )

    for skill in resume.skills:
        story.append(
            Paragraph(
                f"- {_safe_text(skill)}",
                bullet_style,
            )
        )

    story.append(
        Paragraph("Experience", section_style)
    )

    for experience in resume.experience:
        story.append(
            Paragraph(
                f"- {_safe_text(experience)}",
                bullet_style,
            )
        )

    if resume.projects:
        story.append(
            Paragraph("Projects", section_style)
        )

        for project in resume.projects:
            story.append(
                Paragraph(
                    f"- {_safe_text(project)}",
                    bullet_style,
                )
            )

    if resume.education:
        story.append(
            Paragraph("Education", section_style)
        )

        for education in resume.education:
            story.append(
                Paragraph(
                    f"- {_safe_text(education)}",
                    bullet_style,
                )
            )

    document.build(story)