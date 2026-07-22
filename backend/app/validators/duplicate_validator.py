"""Detects duplicate bullet points / entries within the final resume."""
from app.schemas.resume_schema import GeneratedResume


def validate_duplicates(resume: GeneratedResume) -> tuple[bool, list[str]]:
    issues: list[str] = []
    seen: set[str] = set()

    for exp in resume.experience:
        bullets = exp.get("bullets", []) if isinstance(exp, dict) else exp.bullets
        for bullet in bullets:
            key = bullet.strip().lower()
            if key in seen:
                issues.append(f"Duplicate bullet detected: {bullet[:60]}")
            seen.add(key)

    return len(issues) == 0, issues
