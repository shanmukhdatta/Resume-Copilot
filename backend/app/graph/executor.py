"""Retry executor -- re-runs only the specific agents whose section
failed validation, never the entire resume."""
from app.agents.achievements.achievements_agent import AchievementsAgent
from app.agents.certifications.certifications_agent import CertificationsAgent
from app.agents.education.education_agent import EducationAgent
from app.agents.experience.experience_agent import ExperienceAgent
from app.agents.links.links_agent import LinksAgent
from app.agents.projects.projects_agent import ProjectsAgent
from app.agents.skills.skills_agent import SkillsAgent
from app.agents.summary.summary_agent import SummaryAgent
from app.schemas.state_schema import ResumeCopilotState
from app.utils.logger import get_logger

logger = get_logger(__name__)

_AGENTS_BY_SECTION = {
    "summary": SummaryAgent,
    "skills": SkillsAgent,
    "experience": ExperienceAgent,
    "projects": ProjectsAgent,
    "education": EducationAgent,
    "certifications": CertificationsAgent,
    "achievements": AchievementsAgent,
    "links": LinksAgent,
}


async def retry_failed_sections(state: ResumeCopilotState) -> ResumeCopilotState:
    """Re-run generation only for sections implicated by validation
    failures (mapped via the failed_sections list), then re-assemble."""
    from app.nodes.assembly_node import assembly_node

    state.metadata.retry_count += 1
    # Map generic failure categories back to concrete resume sections;
    # if we can't pinpoint one, retry the sections most prone to drift.
    sections_to_retry = set(state.validation.failed_sections) & set(_AGENTS_BY_SECTION)
    if not sections_to_retry:
        sections_to_retry = {"summary", "experience", "skills"}

    logger.info("Retrying sections: %s (attempt %s)", sections_to_retry, state.metadata.retry_count)

    for section in sections_to_retry:
        agent_cls = _AGENTS_BY_SECTION.get(section)
        if agent_cls:
            await agent_cls().run(state)

    return await assembly_node(state)
