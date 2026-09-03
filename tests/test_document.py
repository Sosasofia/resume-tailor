# from pathlib import Path

# from app.document import create_ats_document
# from app.models import ATSResume, JobRequirements, ResumeStrategy
# from app.profile import Basics, ResumeProfile


# def test_markdown_document_includes_resume_and_analysis(tmp_path: Path) -> None:
#     profile = ResumeProfile(
#         basics=Basics(name="Test User", location="Remote", email="test@example.com"),
#         summary="Backend engineer.",
#         skills=["Python"],
#         experience=[],
#         projects=[],
#         education=[],
#     )
#     resume = ATSResume(
#         summary="API-focused engineer.",
#         skills=["Python"],
#         experience=["Built services"],
#         projects=[],
#         education=[],
#     )
#     requirements = JobRequirements(
#         required_skills=["FastAPI"],
#         preferred_skills=[],
#         responsibilities=["Build APIs"],
#         keywords=["REST"],
#     )
#     strategy = ResumeStrategy(
#         priority_skills=["FastAPI"],
#         matching_skills=["python"],
#         missing_required_skills=["fastapi"],
#         relevant_experience=[],
#         relevant_projects=[],
#         keywords_to_use=["REST"],
#     )

#     artifact = create_ats_document(
#         profile,
#         resume,
#         tmp_path / "resume.pdf",
#         output_format="markdown",
#         requirements=requirements,
#         strategy=strategy,
#     )

#     assert artifact == tmp_path / "resume.md"
#     content = artifact.read_text(encoding="utf-8")
#     assert "# Test User" in content
#     assert "API-focused engineer." in content
#     assert "## Job Requirements" in content
#     assert "## Resume Strategy" in content