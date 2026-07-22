"""Pydantic schemas describing the structured job description model."""
from pydantic import BaseModel, Field


class ParsedJobDescription(BaseModel):
    """Structured representation of a parsed job description."""

    title: str = ""
    company: str = ""
    location: str = ""
    seniority: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    raw_text: str = ""
