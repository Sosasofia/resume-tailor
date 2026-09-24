from app.clients.azure_openai import create_client, get_deployment
from app.domain.models import JobRequirements
from app.domain.profile import ResumeProfile


def extract_job_requirements(
    job_description: str,
) -> JobRequirements:
    client = create_client()

    prompt = f"""
Analyze the following job description and extract its requirements.

Rules:

1. required_skills:
   Include concrete technical skills explicitly required by the job.
   Examples:
   - C#
   - .NET
   - PostgreSQL
   - Docker
   - Azure
   - REST APIs

2. preferred_skills:
   Include concrete technical skills described as preferred,
   nice-to-have, or advantageous.

3. responsibilities:
   Describe the main responsibilities of the role.
   These are NOT skills.

4. keywords:
   Include important terminology used by the employer that could
   reasonably matter for ATS matching.

Do not invent requirements that are not present in the job description.

JOB DESCRIPTION:
{job_description}
"""

    response = client.responses.parse(
        model=get_deployment(),
        input=prompt,
        text_format=JobRequirements,
    )

    if response.output_parsed is None:
        raise RuntimeError(
            "The model returned no job requirements."
        )

    return response.output_parsed


def extract_resume_profile(
    resume_text: str
) -> ResumeProfile:
    client = create_client()


    prompt = f"""
Extract the candidate's complete resume information into the
provided schema.


IMPORTANT:
- The resume is the only source of truth.
- Do not invent anything.
- Preserve employers, roles, dates, skills, projects,
  education, certifications, metrics, and achievements.
- Preserve the meaning of the original text.
- If information is missing, use an empty value where the schema
  allows it.
- Do not infer technologies that are not explicitly supported.

RESUME:
{resume_text}
"""
    response = client.responses.parse(
        model=get_deployment(),
        input=prompt,
        text_format=ResumeProfile,
    )

    if response.output_parsed is None:
        raise RuntimeError(
            "The model returned no resume profile."
        )
    
    return response.output_parsed
