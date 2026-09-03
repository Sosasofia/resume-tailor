from pathlib import Path


def load_job_description(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Job description not found: {path}")

    return path.read_text(encoding="utf-8")