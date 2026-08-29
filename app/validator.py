import re

from app.models import ResumeChange, ValidatedChange


TECHNICAL_TERMS = {
    "python",
    "c#",
    ".net",
    "react",
    "angular",
    "javascript",
    "typescript",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "docker",
    "kubernetes",
    "azure",
    "aws",
    "gcp",
    "terraform",
    "redis",
    "kafka",
    "rabbitmq",
    "rest",
    "graphql",
}


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def extract_technical_terms(text: str) -> set[str]:
    normalized = normalize(text)
    found: set[str] = set()

    for term in TECHNICAL_TERMS:
        pattern = rf"(?<!\w){re.escape(term)}(?!\w)"

        if re.search(pattern, normalized):
            found.add(term)

    return found


def extract_numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:[.,]\d+)?%?\b", text))


def extract_years(text: str) -> set[str]:
    return set(re.findall(r"\b(?:19|20)\d{2}\b", text))


def validate_change(
    change: ResumeChange,
    resume_text: str,
) -> ValidatedChange:
    normalized_resume = normalize(resume_text)
    normalized_original = normalize(change.original)

    if normalized_original not in normalized_resume:
        return ValidatedChange(
            change=change,
            approved=False,
            reason="The original text was not found in the source resume.",
        )

    resume_terms = extract_technical_terms(resume_text)
    original_terms = extract_technical_terms(change.original)
    suggested_terms = extract_technical_terms(change.suggested)

    introduced_terms = suggested_terms - original_terms
    unsupported_terms = introduced_terms - resume_terms

    if unsupported_terms:
        return ValidatedChange(
            change=change,
            approved=False,
            reason=(
                "The suggested change introduces unsupported "
                f"technical terms: {sorted(unsupported_terms)}"
            ),
        )

    original_numbers = extract_numbers(change.original)
    suggested_numbers = extract_numbers(change.suggested)

    new_numbers = suggested_numbers - original_numbers

    if new_numbers:
        resume_numbers = extract_numbers(resume_text)
        unsupported_numbers = new_numbers - resume_numbers

        if unsupported_numbers:
            return ValidatedChange(
                change=change,
                approved=False,
                reason=(
                    "The suggested change introduces unsupported "
                    f"numeric claims: {sorted(unsupported_numbers)}"
                ),
            )

    original_years = extract_years(change.original)
    suggested_years = extract_years(change.suggested)

    new_years = suggested_years - original_years

    if new_years:
        resume_years = extract_years(resume_text)
        unsupported_years = new_years - resume_years

        if unsupported_years:
            return ValidatedChange(
                change=change,
                approved=False,
                reason=(
                    "The suggested change introduces unsupported "
                    f"years: {sorted(unsupported_years)}"
                ),
            )

    return ValidatedChange(
        change=change,
        approved=True,
        reason="The proposed change passed validation.",
    )