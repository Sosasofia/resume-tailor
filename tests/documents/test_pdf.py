from pathlib import Path

from pypdf import PdfReader

from app.documents.pdf import create_pdf
from app.domain.models import ATSResume
from app.domain.profile import Basics, ResumeProfile


def test_create_pdf(tmp_path: Path) -> None:
    profile = ResumeProfile(
        basics=Basics(
            name="Test User",
            location="Buenos Aires",
            email="test@example.com",
        ),
        summary="Backend developer with Python experience.",
        skills=["Python", "Docker"],
        experience=[],
        projects=[],
        education=[],
    )

    resume = ATSResume(
        summary="Backend developer with Python experience.",
        skills=["Python", "Docker"],
        experience=["Developed backend services."],
        projects=[],
        education=["Software Engineering"],
    )

    output_path = tmp_path / "resume.pdf"

    create_pdf(
        profile,
        resume,
        output_path,
    )

    assert output_path.exists()

    reader = PdfReader(str(output_path))

    assert len(reader.pages) == 1

    text = reader.pages[0].extract_text()

    assert "Test User" in text
    assert "Python" in text
    assert "Developed backend services." in text