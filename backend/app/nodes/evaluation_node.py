"""Evaluation Node -- computes ATS score, match score, skill gap and
recommendations for the final resume."""
from app.evaluation.ats_score import compute_ats_score
from app.evaluation.keyword_score import compute_keyword_coverage
from app.evaluation.learning_resources import get_learning_resources
from app.evaluation.recommendation import generate_recommendations
from app.evaluation.resume_match import compute_resume_match_score
from app.evaluation.skill_gap import compute_skill_gap
from app.schemas.evaluation_schema import EvaluationReport
from app.schemas.state_schema import ResumeCopilotState
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def evaluation_node(state: ResumeCopilotState) -> ResumeCopilotState:
    state.metadata.current_node = "evaluation"

    ats_score = compute_ats_score(state.final_resume, state.jd)
    match_score = compute_resume_match_score(state.final_resume, state.jd)
    keyword_coverage = compute_keyword_coverage(state.final_resume, state.jd)
    skill_gap = compute_skill_gap(state.final_resume, state.jd)
    recommendations, strengths, weaknesses = generate_recommendations(
        state.final_resume, state.jd, skill_gap, ats_score
    )
    learning_resources = get_learning_resources(skill_gap.missing_skills)

    state.evaluation = EvaluationReport(
        ats_score=ats_score,
        resume_match_score=match_score,
        keyword_coverage=keyword_coverage,
        skill_gap=skill_gap,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        learning_resources=learning_resources,
    )
    logger.info("Evaluation node completed for session %s", state.metadata.session_id)
    return state
