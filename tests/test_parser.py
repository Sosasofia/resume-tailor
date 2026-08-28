from pathlib import Path

import pytest

from app.parser import extract_pdf_text


def test_pdf_must_exist() -> None:
    with pytest.raises(FileNotFoundError):
        extract_pdf_text(Path("does-not-exist.pdf"))


def test_file_must_be_pdf(tmp_path: Path) -> None:
    text_file = tmp_path / "resume.txt"
    text_file.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError):
        extract_pdf_text(text_file)
