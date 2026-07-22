"""Standalone keyword coverage check, reused by both the validation
layer and the evaluation layer."""
from app.llm.embeddings import keyword_overlap
from app.schemas.jd_schema import ParsedJobDescription
from app.schemas.resume_schema import GeneratedResume


def matched_keywords(resume: GeneratedResume, jd: ParsedJobDescription) -> list[str]:
    text_parts = [resume.summary]
    for exp in resume.experience:
        bullets = exp.get("bullets", []) if isinstance(exp, dict) else exp.bullets
        text_parts.extend(bullets)
    full_text = " ".join(text_parts)
    return keyword_overlap(jd.keywords, full_text)
