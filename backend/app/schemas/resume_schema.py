"""Pydantic schemas describing the structured resume data model."""
from pydantic import BaseModel, Field


class ContactLink(BaseModel):
    """A single contact/portfolio link (GitHub, LinkedIn, etc.)."""

    label: str
    url: str


class ContactInfo(BaseModel):
    """Candidate contact information."""

    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    links: list[ContactLink] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""
    details: list[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    company: str = ""
    title: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    bullets: list[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)
    link: str = ""


class CertificationEntry(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""


class AchievementEntry(BaseModel):
    title: str = ""
    description: str = ""
    date: str = ""


class SkillCategory(BaseModel):
    category: str = "General"
    skills: list[str] = Field(default_factory=list)


class ParsedResume(BaseModel):
    """Raw structured resume extracted from the uploaded document.
    Nothing in this model is AI-generated; it is a faithful structured
    representation of what the candidate actually submitted."""

    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str = ""
    skills: list[SkillCategory] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)
    achievements: list[AchievementEntry] = Field(default_factory=list)
    raw_text: str = ""


class GeneratedResume(BaseModel):
    """Final tailored resume assembled from all agent outputs."""

    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str = ""
    skills: list[SkillCategory] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)
    achievements: list[AchievementEntry] = Field(default_factory=list)
    links: list[ContactLink] = Field(default_factory=list)
