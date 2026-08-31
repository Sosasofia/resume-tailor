from pathlib import Path

from app.document import create_ats_document
from app.llm import extract_job_requirements, generate_ats_resume
from app.profile_loader import load_profile
from app.strategy import build_resume_strategy


def main() -> None:
    profile_path = Path("data/profile.json")
    job_path = Path("data/input/job_description.txt")
    output_path = Path("output/tailored_resume.pdf")

    if not job_path.exists():
        raise FileNotFoundError(f"Job description not found: {job_path}")

    profile = load_profile(profile_path)
    job_description = job_path.read_text(encoding="utf-8")

    requirements = extract_job_requirements(
        job_description
    )

    strategy = build_resume_strategy(
        profile,
        requirements,
    )

    print("=== JOB REQUIREMENTS ===")

    print("\nRequired skills:")
    for skill in requirements.required_skills:
        print(f"- {skill}")

    print("\nPreferred skills:")
    for skill in requirements.preferred_skills:
        print(f"- {skill}")

    print("\n=== MATCHING SKILLS ===")
    for skill in strategy.matching_skills:
        print(f"- {skill}")

    print("\n=== MISSING REQUIRED SKILLS ===")
    for skill in strategy.missing_required_skills:
        print(f"- {skill}")

    ats_resume = generate_ats_resume(
        profile,
        requirements,
        strategy,
    )

    print("\n=== GENERATED ATS RESUME ===")

    print("\nSUMMARY")
    print(ats_resume.summary)

    print("\nSKILLS")
    for skill in ats_resume.skills:
        print(f"- {skill}")

    print("\nEXPERIENCE")
    for experience in ats_resume.experience:
        print(f"- {experience}")

    print("\nPROJECTS")
    for project in ats_resume.projects:
        print(f"- {project}")

    print("\nEDUCATION")
    for education in ats_resume.education:
        print(f"- {education}")

    create_ats_document(
        profile=profile,
        resume=ats_resume,
        output_path=output_path,
    )

    print(f"\nResume written to: {output_path}")


if __name__ == "__main__":
    main()