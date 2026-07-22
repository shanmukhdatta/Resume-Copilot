"""Schema for the AI planning & analysis layer's output. The planner
NEVER generates resume content -- only a generation strategy."""
from pydantic import BaseModel, Field


class SectionPlan(BaseModel):
    """Generation guidance for a single resume section."""

    section: str
    priority: int = 5
    focus_points: list[str] = Field(default_factory=list)
    keywords_to_emphasize: list[str] = Field(default_factory=list)


class PlanningOutput(BaseModel):
    detected_role: str = ""
    seniority_level: str = ""
    ats_keywords: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    ranked_projects: list[str] = Field(default_factory=list)
    ranked_experience: list[str] = Field(default_factory=list)
    section_plans: list[SectionPlan] = Field(default_factory=list)
    overall_strategy: str = ""
