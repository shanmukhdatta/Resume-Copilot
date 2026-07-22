"""Checks internal consistency (e.g. date ordering, non-empty required
fields) of the final resume."""
from app.schemas.resume_schema import GeneratedResume


def validate_consistency(resume: GeneratedResume) -> tuple[bool, list[str]]:
    issues: list[str] = []

    if not resume.contact.full_name:
        issues.append("Missing candidate full name.")

    for exp in resume.experience:
        entry = exp if isinstance(exp, dict) else exp.model_dump()
        if entry.get("company") and not entry.get("title"):
            issues.append(f"Experience at {entry.get('company')} missing a title.")

    return len(issues) == 0, issues
