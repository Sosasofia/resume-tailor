import json
from pathlib import Path

from app.domain.profile import ResumeProfile


def load_profile(path: Path) -> ResumeProfile:
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return ResumeProfile.model_validate(data)