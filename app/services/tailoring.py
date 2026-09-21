from app.clients.azure_openai import create_client, get_deployment
from app.services import validation
from app.domain.models import ATSResume, JobRequirements, ResumeStrategy
from app.domain.profile import ResumeProfile
from app.services.matching import build_resume_strategy


class TailoringValidationError(Exception):
    def __init__(
        self,
        stage: str,
        errors: list[str] | None = None,
        issues: list[dict] | None = None,
    ):
        self.stage = stage
        self.errors = errors or []
        self.issues = issues or []

        super().__init__(
            f"Tailored resume failed {stage} validation."
        )


def generate_validated_resume(
    profile: ResumeProfile,
    requirements: JobRequirements,
    strategy: ResumeStrategy,
) -> ATSResume:
    max_attempts = 2
    attempts = 1
    previous_errors = None

    while attempts <= max_attempts:
    
        resume = generate_ats_resume(
            profile,
            requirements,
            strategy,
            previous_errors=previous_errors,
        )

        deterministic_result = validation.validate_resume(
            profile,
            resume,
        )

        previous_errors = deterministic_result.errors

        if deterministic_result.approved:
            break

        if attempts == max_attempts:
            raise TailoringValidationError(
                stage="deterministic_factuality",
                errors=deterministic_result.errors,
            )

        previous_errors = deterministic_result.errors
        attempts += 1

    factuality_result = validation.validate_factuality(
        profile,
        resume,
    )

    if not factuality_result.approved:
        raise TailoringValidationError(
            stage="semantic_factuality",
            issues=[
                issue.model_dump()
                for issue in factuality_result.issues
            ],
        )

    return resume


def generate_ats_resume(
    profile: ResumeProfile,
    requirements: JobRequirements,
    strategy: ResumeStrategy,
    previous_errors: list[str] | None = None,
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
- Every statement in the summary must be directly supported by
  one or more facts in the candidate profile.
- Avoid generic claims such as "strong foundation", "extensive
  experience", "proven expertise", "data-driven", or similar
  evaluative language unless the profile explicitly supports them.
- Do not combine separate profile facts into a broader claim if
  that broader claim introduces a new concept.
- Prefer concrete facts over subjective descriptions.

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

"""
    if previous_errors:
        prompt += "\nCORRECTION REQUIRED:\nYour previous attempt failed strict validation because you included the following unsupported facts/skills:\n"
        for error in previous_errors:
            prompt += f"- {error}\n"
        prompt += "\nRegenerate the complete ATS-friendly resume, ensuring you DO NOT include these unsupported items."
    else:
        prompt += "\nReturn the complete ATS-friendly resume."

    response = client.responses.parse(
        model=get_deployment(),
        input=prompt,
        text_format=ATSResume,
    )

    if response.output_parsed is None:
        raise RuntimeError(
            "The model returned no ATS resume."
        )

    return response.output_parsed


def tailor_resume(
    profile: ResumeProfile,
    requirements: JobRequirements,
) -> ATSResume:
    strategy = build_resume_strategy(
        profile,
        requirements,
    )

    return generate_validated_resume(
        profile,
        requirements,
        strategy,
    )