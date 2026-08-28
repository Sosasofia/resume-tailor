from pathlib import Path

import pymupdf


def extract_pdf_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Resume not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {path}")

    document = pymupdf.open(path)

    try:
        pages = [page.get_text() for page in document]
    finally:
        document.close()

    return "\n".join(pages).strip()
