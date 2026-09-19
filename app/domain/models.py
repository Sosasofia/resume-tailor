from pydantic import BaseModel


class JobRequirements(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    responsibilities: list[str]
    keywords: list[str]


class ResumeStrategy(BaseModel):
    priority_skills: list[str]
    matching_skills: list[str]
    missing_required_skills: list[str]
    relevant_experience: list[str]
    relevant_projects: list[str]
    keywords_to_use: list[str]


class ATSResume(BaseModel):
    summary: str
    skills: list[str]
    experience: list[str]
    projects: list[str]
    education: list[str]


class FactualityIssue(BaseModel):
    section: str
    claim: str
    reason: str


class FactualityResult(BaseModel):
    approved: bool
    issues: list[FactualityIssue]
