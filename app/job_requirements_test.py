from pathlib import Path

from app.llm import extract_job_requirements


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    job_description = read_text_file(
        Path("data/input/job_description.txt")
    )

    requirements = extract_job_requirements(
        job_description
    )

    print("=== REQUIRED SKILLS ===")
    for skill in requirements.required_skills:
        print(f"- {skill}")

    print("\n=== PREFERRED SKILLS ===")
    for skill in requirements.preferred_skills:
        print(f"- {skill}")

    print("\n=== RESPONSIBILITIES ===")
    for responsibility in requirements.responsibilities:
        print(f"- {responsibility}")

    print("\n=== ATS KEYWORDS ===")
    for keyword in requirements.keywords:
        print(f"- {keyword}")


if __name__ == "__main__":
    main()