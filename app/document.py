from pathlib import Path
import typst

from app.models import ATSResume
from app.profile import ResumeProfile


def escape_typst(text: str) -> str:
    """Escapes special Typst characters to prevent compilation errors."""
    if not text:
        return ""
    
    special_chars = ["#", "$", "<", ">", "@", "*", "_", "`"]
    
    escaped_text = text
    for char in special_chars:
        escaped_text = escaped_text.replace(char, f"\\{char}")
        
    return escaped_text


def create_ats_document(
    profile: ResumeProfile,
    resume: ATSResume,
    output_path: Path,
) -> None:
    contact_info = [
        escape_typst(profile.basics.location), 
        escape_typst(profile.basics.email)
    ]
    
    if profile.basics.linkedin:
        contact_info.append(escape_typst(profile.basics.linkedin))
    if profile.basics.github:
        contact_info.append(escape_typst(profile.basics.github))
        
    contact_str = " | ".join(contact_info)
    
    typst_content = f"""
#set page(margin: (x: 1in, y: 1in))
#set text(font: "Arial", size: 10pt)
#set par(justify: true)

#align(center)[
  = {escape_typst(profile.basics.name)}
  {contact_str}
]

== Summary
{escape_typst(resume.summary)}

== Skills
"""
    for skill in resume.skills:
        typst_content += f"- {escape_typst(skill)}\n"

    typst_content += "\n== Experience\n"
    for exp in resume.experience:
        typst_content += f"- {escape_typst(exp)}\n"

    typst_content += "\n== Projects\n"
    for proj in resume.projects:
        typst_content += f"- {escape_typst(proj)}\n"

    typst_content += "\n== Education\n"
    for edu in resume.education:
        typst_content += f"- {escape_typst(edu)}\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    typst_path = output_path.with_suffix(".typ")
    typst_path.write_text(typst_content, encoding="utf-8")
    
    pdf_path = output_path.with_suffix(".pdf")
    typst.compile(str(typst_path), output=str(pdf_path))