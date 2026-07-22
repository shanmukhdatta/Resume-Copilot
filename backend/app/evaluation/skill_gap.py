"""Computes a skill-gap report: matched vs missing JD skills."""
from rapidfuzz import fuzz

from app.schemas.evaluation_schema import SkillGapReport
from app.schemas.jd_schema import ParsedJobDescription
from app.schemas.resume_schema import GeneratedResume


def _all_resume_skills(resume: GeneratedResume) -> list[str]:
    names: list[str] = []
    for cat in resume.skills:
        entries = cat.get("skills", []) if isinstance(cat, dict) else cat.skills
        names.extend(entries)
    return [n.lower() for n in names]


def compute_skill_gap(resume: GeneratedResume, jd: ParsedJobDescription) -> SkillGapReport:
    required = jd.required_skills + jd.preferred_skills
    resume_skills = _all_resume_skills(resume)

    matched, missing = [], []
    for skill in required:
        if any(fuzz.ratio(skill.lower(), rs) > 80 for rs in resume_skills):
            matched.append(skill)
        else:
            missing.append(skill)

    gap_pct = round((len(missing) / len(required)) * 100, 1) if required else 0.0
    return SkillGapReport(matched_skills=matched, missing_skills=missing, gap_percentage=gap_pct)
