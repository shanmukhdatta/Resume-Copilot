"""Computes JD keyword coverage percentage for the final resume."""
from app.validators.keyword_validator import matched_keywords
from app.schemas.jd_schema import ParsedJobDescription
from app.schemas.resume_schema import GeneratedResume


def compute_keyword_coverage(resume: GeneratedResume, jd: ParsedJobDescription) -> float:
    if not jd.keywords:
        return 0.0
    matched = matched_keywords(resume, jd)
    return round((len(matched) / len(jd.keywords)) * 100, 1)
