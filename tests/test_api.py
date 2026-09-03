# import json

# from fastapi.testclient import TestClient

# from app import api
# from app.models import ATSResume, JobRequirements, ResumeStrategy


# client = TestClient(api.app)


# def test_extract_job_description(monkeypatch) -> None:
#     expected = JobRequirements(
#         required_skills=["Python"],
#         preferred_skills=[],
#         responsibilities=["Build APIs"],
#         keywords=["REST"],
#     )
#     monkeypatch.setattr(api, "extract_job_requirements", lambda text: expected)

#     response = client.post(
#         "/extract",
#         data={"document_type": "job_description"},
#         files={"document": ("job.md", "Build APIs with Python", "text/markdown")},
#     )

#     assert response.status_code == 200
#     assert response.json() == expected.model_dump()


# def test_tailor_markdown_with_typed_inputs(monkeypatch) -> None:
#     profile = {
#         "basics": {"name": "Test User", "location": "Remote", "email": "test@example.com"},
#         "summary": "Backend engineer.",
#         "skills": ["Python"],
#         "experience": [],
#         "projects": [],
#         "education": [],
#     }
#     requirements = JobRequirements(
#         required_skills=[], preferred_skills=[], responsibilities=[], keywords=[]
#     )
#     resume = ATSResume(summary="Generated", skills=[], experience=[], projects=[], education=[])
#     strategy = ResumeStrategy(
#         priority_skills=[], matching_skills=[], missing_required_skills=[],
#         relevant_experience=[], relevant_projects=[], keywords_to_use=[]
#     )
#     monkeypatch.setattr(api, "tailor_resume", lambda profile, description, requirements: (resume, requirements, strategy))

#     response = client.post(
#         "/tailor",
#         data={
#             "format": "markdown",
#             "profile_json": json.dumps(profile),
#             "job_requirements_json": requirements.model_dump_json(),
#         },
#     )

#     assert response.status_code == 200
#     assert response.headers["content-type"].startswith("text/markdown")
#     assert "Generated" in response.text


# def test_tailor_requires_one_source_each() -> None:
#     response = client.post("/tailor", data={"format": "markdown"})
#     assert response.status_code == 400