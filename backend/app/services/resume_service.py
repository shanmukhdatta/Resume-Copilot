"""Orchestration service tying together upload resolution, the
LangGraph workflow, and session caching -- the main entry point called
by the /generate API route."""
from app.graph.workflow import run_resume_workflow
from app.schemas.state_schema import (
    FileMetadata,
    GraphMetadata,
    ResumeCopilotState,
)
from app.services.cache_service import cache_session
from app.utils.helpers import new_id
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def generate_resume(resume_path: str, jd_path: str, user_notes: str, template: str) -> ResumeCopilotState:
    session_id = new_id("session")

    initial_state = ResumeCopilotState(
        files=FileMetadata(resume_path=resume_path, jd_path=jd_path),
        metadata=GraphMetadata(session_id=session_id, template=template),
        user_notes=user_notes,
    )

    logger.info("Starting resume generation workflow for session %s", session_id)
    final_state = await run_resume_workflow(initial_state)
    cache_session(session_id, final_state)
    return final_state
