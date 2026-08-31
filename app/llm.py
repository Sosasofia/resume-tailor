import os

from openai import OpenAI

from app.models import JobRequirements, ATSResume, ResumeStrategy
from app.profile import ResumeProfile

def create_client() -> OpenAI:
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    api_key = os.environ["AZURE_OPENAI_API_KEY"]

    return OpenAI(
        base_url=endpoint,
        api_key=api_key,
    )



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
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        input=prompt,
        text_format=JobRequirements,
    )

    if response.output_parsed is None:
        raise RuntimeError(
            "The model returned no job requirements."
        )

    return response.output_parsed



def generate_ats_resume(
    profile: ResumeProfile,
    requirements: JobRequirements,
    strategy: ResumeStrategy,
) -> ATSResume:
    client = create_client()

    prompt = f"""
Create an ATS-friendly resume for the candidate.

IMPORTANT: 
You are an expert ATS optimization engine. Your goal is to actively rewrite and reframe the candidate's existing experience to maximize alignment with the job description.

SOURCE OF TRUTH:
The candidate's profile is the only authoritative source of
candidate facts.

STRICT RULES:
- Never invent a skill, technology, employer, title, date,
  achievement, metric, certification, education, or responsibility.
- Never add a missing required skill as if the candidate has it.
- Use only facts present in the candidate profile.
- Prioritize information relevant to the target job.
- Use terminology from the job description when it accurately
  describes something already supported by the profile.
- Preserve important metrics and achievements from the profile.
- Do not fabricate metrics.
- Do not fabricate experience.
- Do not add a "References" section.
- Keep the resume concise and ATS-friendly.

ATS FORMAT:
- Standard section names.
- Plain text.
- No tables.
- No columns.
- No icons.
- No graphics.
- No decorative symbols.
- Use concise professional bullet points.

TARGET JOB REQUIREMENTS:
{requirements.model_dump_json(indent=2)}

RESUME STRATEGY:
{strategy.model_dump_json(indent=2)}

CANDIDATE PROFILE:
{profile.model_dump_json(indent=2)}

Return the complete ATS-friendly resume.
"""

    response = client.responses.parse(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        input=prompt,
        text_format=ATSResume,
    )

    if response.output_parsed is None:
        raise RuntimeError(
            "The model returned no ATS resume."
        )

    return response.output_parsed