"""Checks that the final resume covers key ATS keywords from the JD."""
from app.llm.embeddings import keyword_overlap
from app.schemas.jd_schema import ParsedJobDescription
from app.schemas.resume_schema import GeneratedResume


def _resume_full_text(resume: GeneratedResume) -> str:
    parts = [resume.summary]
    for cat in resume.skills:
        parts.extend(cat.get("skills", []) if isinstance(cat, dict) else [])
    for exp in resume.experience:
        parts.extend(exp.get("bullets", []) if isinstance(exp, dict) else [])
    for proj in resume.projects:
        parts.extend(proj.get("bullets", []) if isinstance(proj, dict) else [])
    return " ".join(str(p) for p in parts if p)


def validate_ats(resume: GeneratedResume, jd: ParsedJobDescription) -> tuple[bool, list[str]]:
    """Returns (passed, issues). Fails if keyword coverage is too low."""
    if not jd.keywords:
        return True, []

    text = _resume_full_text(resume)
    matched = keyword_overlap(jd.keywords, text)
    coverage = (len(matched) / len(jd.keywords)) * 100 if jd.keywords else 100.0

    issues = []
    if coverage < 30:
        issues.append(f"Low ATS keyword coverage: {coverage:.1f}%")
    return len(issues) == 0, issues
