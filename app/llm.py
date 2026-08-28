import os

from openai import OpenAI

from app.models import JobAnalysis, TailoringResult


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

def tailor_resume(
    resume_text: str,
    job_description: str,
    analysis: JobAnalysis,
) -> TailoringResult:
    client = create_client()

    prompt = f"""
Analyze the candidate's resume against the job description.

You are proposing edits, not inventing information.

STRICT RULES:
- Only use information already present in the resume.
- Never invent technologies, responsibilities, employers,
  job titles, education, certifications, achievements, or
  years of experience.
- Do not claim experience with a skill simply because the job
  description requests it.
- Preserve factual meaning.
- Prefer rewriting existing statements over creating new claims.
- If there is no legitimate change to make, return an empty
  changes list.
- Keep suggested text concise and appropriate for a professional
  resume.

For every proposed change:
- section: resume section being changed
- original: exact or near-exact existing text
- suggested: revised version
- reason: why the change improves alignment with the job description

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

EXISTING ANALYSIS:
{analysis.model_dump_json(indent=2)}
"""

    response = client.responses.parse(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        input=prompt,
        text_format=TailoringResult,
    )

    if response.output_parsed is None:
        raise RuntimeError("The model returned no structured analysis.")

    return response.output_parsed