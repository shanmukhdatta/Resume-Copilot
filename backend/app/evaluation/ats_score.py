"""Computes an overall ATS compatibility score (0-100)."""
from app.evaluation.keyword_score import compute_keyword_coverage
from app.schemas.jd_schema import ParsedJobDescription
from app.schemas.resume_schema import GeneratedResume


def compute_ats_score(resume: GeneratedResume, jd: ParsedJobDescription) -> float:
    """Weighted score combining keyword coverage and structural completeness."""
    keyword_coverage = compute_keyword_coverage(resume, jd)

    completeness_checks = [
        bool(resume.contact.full_name),
        bool(resume.summary),
        bool(resume.skills),
        bool(resume.experience),
        bool(resume.education),
    ]
    completeness_score = (sum(completeness_checks) / len(completeness_checks)) * 100

    return round(0.7 * keyword_coverage + 0.3 * completeness_score, 1)
