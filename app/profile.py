from pydantic import BaseModel, Field


class Basics(BaseModel):
    name: str
    location: str
    email: str
    linkedin: str = ""
    github: str = ""


class Experience(BaseModel):
    company: str
    role: str
    location: str
    start_year: int
    end_year: int | None = None
    achievements: list[str]


class Project(BaseModel):
    name: str
    year: int | None = None
    description: str
    achievements: list[str] = []


class Education(BaseModel):
    institution: str
    location: str
    degree: str
    start_year: int
    end_year: int | None = None


class ResumeProfile(BaseModel):
    basics: Basics
    summary: str
    skills: list[str]
    experience: list[Experience]
    projects: list[Project]
    education: list[Education]
    certifications: list[str] = Field(default_factory=list)