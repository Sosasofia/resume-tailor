import os

from openai import OpenAI

from app.models import JobAnalysis


def create_client() -> OpenAI:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    api_key = os.environ["AZURE_OPENAI_API_KEY"]

    return OpenAI(
        base_url=endpoint,
        api_key=api_key,
    )


def analyze_job(
    resume_text: str,
    job_description: str,
) -> JobAnalysis:
    client = create_client()

    prompt = f"""
Analyze the candidate's resume against the job description.

Rules:
- matching_skills: technologies, frameworks, programming languages,
  databases, tools, or technical competencies explicitly supported
  by the resume.
- missing_skills: technical skills explicitly required by the job
  description but not supported by the resume.
- matching_experience: relevant experience or responsibilities
  demonstrated by the resume.
- recommendations: concrete suggestions for improving the resume.
- Never invent experience, skills, companies, education, or
  qualifications that are not present in the resume.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

    response = client.responses.parse(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        input=prompt,
        text_format=JobAnalysis,
    )

    if response.output_parsed is None:
        raise RuntimeError("The model returned no structured analysis.")

    return response.output_parsed