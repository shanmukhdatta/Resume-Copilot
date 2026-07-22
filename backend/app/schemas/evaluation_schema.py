"""Schemas describing AI evaluation / scoring output."""
from pydantic import BaseModel, Field

from app.evaluation.learning_resources import SkillResourceSuggestion


class SkillGapReport(BaseModel):
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    gap_percentage: float = 0.0


class EvaluationReport(BaseModel):
    ats_score: float = 0.0
    resume_match_score: float = 0.0
    keyword_coverage: float = 0.0
    skill_gap: SkillGapReport = Field(default_factory=SkillGapReport)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    # Concrete "close the gap" resources for each missing skill -- see
    # app/evaluation/learning_resources.py for why these are curated
    # links rather than LLM-generated course names.
    learning_resources: list[SkillResourceSuggestion] = Field(default_factory=list)
