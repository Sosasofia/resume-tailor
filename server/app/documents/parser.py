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


def extract_markdown_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")
    if path.suffix.lower() not in {".md", ".markdown", ".txt"}:
        raise ValueError(f"Expected a Markdown or text file: {path}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Document is empty: {path}")
    return text


def extract_document_text(path: Path) -> str:
    text = extract_pdf_text(path) if path.suffix.lower() == ".pdf" else extract_markdown_text(path)
    if not text:
        raise ValueError(f"Document contains no extractable text: {path}")
    return text
