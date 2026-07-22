"""Assembly Node -- merges all parallel agent outputs into the final
Generated Resume JSON."""
from app.schemas.resume_schema import GeneratedResume
from app.schemas.state_schema import ResumeCopilotState
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def assembly_node(state: ResumeCopilotState) -> ResumeCopilotState:
    state.metadata.current_node = "assembly"
    sections = state.generated_sections

    state.final_resume = GeneratedResume(
        contact=state.resume.contact,
        summary=sections.summary or state.resume.summary,
        skills=sections.skills or [s.model_dump() for s in state.resume.skills],
        experience=sections.experience or [e.model_dump() for e in state.resume.experience],
        projects=sections.projects or [p.model_dump() for p in state.resume.projects],
        education=sections.education or [e.model_dump() for e in state.resume.education],
        certifications=sections.certifications
        or [c.model_dump() for c in state.resume.certifications],
        achievements=sections.achievements
        or [a.model_dump() for a in state.resume.achievements],
        links=sections.links or [l.model_dump() for l in state.resume.contact.links],
    )
    logger.info("Assembly node merged sections for session %s", state.metadata.session_id)
    return state
