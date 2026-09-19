from app.domain.models import ATSResume, FactualityResult
from app.domain.profile import ResumeProfile
from app.clients.azure_openai import create_client, get_deployment


class ValidationResult:
    def __init__(
        self,
        approved: bool,
        errors: list[str],
    ):
        self.approved = approved
        self.errors = errors


def validate_resume(
    profile: ResumeProfile,
    resume: ATSResume,
) -> ValidationResult:
    errors: list[str] = []

    errors.extend(_validate_skills(profile, resume))
    errors.extend(_validate_education(profile, resume))

    return ValidationResult(
        approved=not errors,
        errors=errors,
    )


def validate_factuality(
    profile: ResumeProfile,
    resume: ATSResume,
) -> FactualityResult:
    client = create_client()

    prompt = f"""
Determine whether the generated ATS resume contains only facts
supported by the candidate's master resume profile.

The candidate profile is the ONLY source of truth.

A generated statement does NOT need to use the exact same wording
as the profile. Legitimate paraphrasing and concise rewriting are
allowed.

However, reject any claim that introduces information that is not
supported by the profile.

STRICT RULES:

1. Do not assume facts that are merely plausible.
2. Do not use general industry knowledge as evidence.
3. Do not infer technologies from a role or responsibility.
4. Do not infer responsibilities from a technology.
5. Do not infer seniority from job title unless supported.
6. Do not infer achievements, metrics, scale, or impact.
7. Do not infer employers, roles, dates, education, or certifications.
8. Do not treat a job requirement as evidence that the candidate
   possesses that skill.
9. Paraphrasing is allowed when the underlying claim is clearly
   supported by the profile.
10. If a claim is ambiguous and cannot be confidently supported
    by the profile, reject it.

Examples:

PROFILE:
Skills: Python, SQL, Docker

GENERATED:
"Python, SQL, Docker"
=> supported

GENERATED:
"Python, SQL, Docker, Kubernetes"
=> unsupported because Kubernetes is not in the profile.

PROFILE:
"Designed and developed a microservices architecture."

GENERATED:
"Designed and implemented a microservices architecture."
=> supported paraphrasing.

GENERATED:
"Designed and implemented a Kubernetes-based microservices
architecture."
=> unsupported because Kubernetes is not established by the profile.

PROFILE:
"Improved signup rate by 15%."

GENERATED:
"Increased signup conversion by 15%."
=> potentially supported if the statement preserves the same fact.

GENERATED:
"Increased signup rate by 30%."
=> unsupported because the metric changed.

Return:
- approved=true only when the generated resume contains no
  unsupported factual claims.
- approved=false when one or more claims are unsupported.
- For every unsupported claim, provide its section, the claim,
  and a concise explanation.

CANDIDATE PROFILE:
{profile.model_dump_json(indent=2)}

GENERATED ATS RESUME:
{resume.model_dump_json(indent=2)}
"""

    response = client.responses.parse(
        model=get_deployment(),
        input=prompt,
        text_format=FactualityResult,
    )

    if response.output_parsed is None:
        raise RuntimeError(
            "The model returned no factuality result."
        )

    return response.output_parsed


def _validate_skills(
    profile: ResumeProfile,
    resume: ATSResume,
) -> list[str]:
    errors = []

    allowed_skills = {
        skill.strip().lower()
        for skill in profile.skills
    }

    for skill in resume.skills:
        if skill.strip().lower() not in allowed_skills:
            errors.append(
                f"Unsupported skill: {skill}"
            )

    return errors


def _validate_education(
    profile: ResumeProfile,
    resume: ATSResume,
) -> list[str]:
    errors = []

    institutions = {
        education.institution.strip().lower()
        for education in profile.education
    }

    for claim in resume.education:
        normalized = claim.strip().lower()

        if not any(
            institution in normalized
            for institution in institutions
        ):
            errors.append(
                f"Unsupported education claim: {claim}"
            )

    return errors
