from pathlib import Path

from analyzer import compare_skills
from parser import extract_pdf_text


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    resume_path = Path("data/input/data.pdf")
    job_description_path = Path("data/input/job_description.txt")

    resume = extract_pdf_text(resume_path)
    job_description = read_text_file(job_description_path)

    matching_skills, missing_skills = compare_skills(
        resume,
        job_description,
    )

    print("=== MATCHING SKILLS ===")
    for skill in sorted(matching_skills):
        print(f"- {skill}")

    print("\n=== MISSING SKILLS ===")
    for skill in sorted(missing_skills):
        print(f"- {skill}")


if __name__ == "__main__":
    main()
