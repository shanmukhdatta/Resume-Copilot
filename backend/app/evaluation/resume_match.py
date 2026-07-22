"""Computes an overall resume-to-JD match score using fuzzy text
similarity across the full resume vs the full JD."""
from app.llm.embeddings import text_similarity
from app.schemas.jd_schema import ParsedJobDescription
from app.schemas.resume_schema import GeneratedResume


def _resume_text(resume: GeneratedResume) -> str:
    parts = [resume.summary]
    for exp in resume.experience:
        bullets = exp.get("bullets", []) if isinstance(exp, dict) else exp.bullets
        parts.extend(bullets)
    for proj in resume.projects:
        bullets = proj.get("bullets", []) if isinstance(proj, dict) else proj.bullets
        parts.extend(bullets)
    return " ".join(str(p) for p in parts if p)


def compute_resume_match_score(resume: GeneratedResume, jd: ParsedJobDescription) -> float:
    resume_text = _resume_text(resume)
    jd_text = " ".join(jd.responsibilities + jd.qualifications) or jd.raw_text
    if not resume_text or not jd_text:
        return 0.0
    return round(text_similarity(resume_text, jd_text), 1)
