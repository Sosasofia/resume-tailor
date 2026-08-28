from pydantic import BaseModel, Field

class JobAnalysis(BaseModel):
    match_score: float = Field(ge=0.0, le=1.0)
    matching_skills: list[str]
    missing_skills: list[str]
    matching_experience: list[str]
    recommendations: list[str]