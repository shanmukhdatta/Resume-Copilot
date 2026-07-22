"""Generates human-readable strengths, weaknesses, and recommendations
from the computed evaluation metrics."""
from app.schemas.evaluation_schema import SkillGapReport
from app.schemas.jd_schema import ParsedJobDescription
from app.schemas.resume_schema import GeneratedResume


def generate_recommendations(
    resume: GeneratedResume,
    jd: ParsedJobDescription,
    skill_gap: SkillGapReport,
    ats_score: float,
) -> tuple[list[str], list[str], list[str]]:
    recommendations: list[str] = []
    strengths: list[str] = []
    weaknesses: list[str] = []

    if ats_score >= 75:
        strengths.append("Strong ATS keyword alignment with the job description.")
    elif ats_score >= 50:
        weaknesses.append("Moderate ATS keyword alignment; some key terms are missing.")
        recommendations.append("Incorporate more JD-specific keywords into your summary and bullets.")
    else:
        weaknesses.append("Low ATS keyword alignment with this job description.")
        recommendations.append("Significantly tailor skills and experience wording toward the JD's key terms.")

    if skill_gap.missing_skills:
        weaknesses.append(f"Missing skills relevant to the role: {', '.join(skill_gap.missing_skills[:5])}")
        recommendations.append(
            "Consider highlighting transferable experience or upskilling in: "
            + ", ".join(skill_gap.missing_skills[:5])
        )
    else:
        strengths.append("Your skill set covers the job description's key requirements.")

    if len(resume.experience) == 0:
        weaknesses.append("No experience entries found in the resume.")
    if len(resume.projects) >= 1:
        strengths.append("Relevant projects are present to demonstrate hands-on skills.")

    return recommendations, strengths, weaknesses
