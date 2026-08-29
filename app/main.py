from pathlib import Path

from app.llm import analyze_job, tailor_resume
from app.parser import extract_pdf_text
from app.validator import validate_change


def read_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text(encoding="utf-8")


def main() -> None:
    resume_path = Path("data/input/data.pdf")
    job_description_path = Path("data/input/job_description.txt")

    resume_text = extract_pdf_text(resume_path)
    job_description = read_text_file(job_description_path)

    analysis = analyze_job(
        resume_text,
        job_description,
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

    tailoring = tailor_resume(
        resume_text,
        job_description,
        analysis,
    )

    validated_changes = [
        validate_change(change, resume_text)
        for change in tailoring.changes
    ]

    print("\n=== APPROVED RESUME CHANGES ===")

    approved_changes = [
        result for result in validated_changes
        if result.approved
    ]

    if not approved_changes:
        print("No changes passed validation.")
    else:
        for index, result in enumerate(approved_changes, start=1):
            change = result.change

            print(f"\n[{index}] {change.section}")
            print(f"Original:   {change.original}")
            print(f"Suggested:  {change.suggested}")
            print(f"Reason:     {change.reason}")

    print("\n=== REJECTED RESUME CHANGES ===")

    rejected_changes = [
        result for result in validated_changes
        if not result.approved
    ]

    if not rejected_changes:
        print("No changes were rejected.")
    else:
        for index, result in enumerate(rejected_changes, start=1):
            change = result.change

            print(f"\n[{index}] {change.section}")
            print(f"Original:   {change.original}")
            print(f"Suggested:  {change.suggested}")
            print(f"Reason:     {result.reason}")


if __name__ == "__main__":
    main()