from pathlib import Path

from app.llm import analyze_job
from app.parser import extract_pdf_text


def read_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    return path.read_text(encoding="utf-8")


def main() -> None:
    resume_path = Path("data/input/data.pdf")
    job_description_path = Path("data/input/job_description.txt")

    resume = extract_pdf_text(resume_path)
    job_description = read_text_file(job_description_path)

    analysis = analyze_job(
        resume_text=resume,
        job_description=job_description,
    )

    print("=== MATCH SCORE ===")
    print(f"{analysis.match_score:.0%}")

    print("\n=== MATCHING SKILLS ===")
    for skill in analysis.matching_skills:
        print(f"- {skill}")

    print("\n=== MISSING SKILLS ===")
    for skill in analysis.missing_skills:
        print(f"- {skill}")

    print("\n=== MATCHING EXPERIENCE ===")
    for experience in analysis.matching_experience:
        print(f"- {experience}")

    print("\n=== RECOMMENDATIONS ===")
    for recommendation in analysis.recommendations:
        print(f"- {recommendation}")


if __name__ == "__main__":
    main()
