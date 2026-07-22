"""Schemas for the validation layer's pass/fail reporting."""
from pydantic import BaseModel, Field


class SectionValidationResult(BaseModel):
    section: str
    passed: bool = True
    issues: list[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    """Aggregated validation results across all resume sections."""

    overall_passed: bool = True
    schema_valid: bool = True
    ats_valid: bool = True
    grammar_valid: bool = True
    hallucination_free: bool = True
    consistent: bool = True
    duplicate_free: bool = True
    section_results: list[SectionValidationResult] = Field(default_factory=list)
    failed_sections: list[str] = Field(default_factory=list)
    retry_count: int = 0
