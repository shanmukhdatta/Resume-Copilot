"""Parser Node -- parses resume + JD files into structured JSON, and
builds the initial shared LangGraph state."""
from app.parsers.jd.jd_parser import parse_job_description
from app.parsers.parser_factory import parse_resume
from app.schemas.state_schema import ResumeCopilotState
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def parser_node(state: ResumeCopilotState) -> ResumeCopilotState:
    state.metadata.current_node = "parser"
    try:
        state.resume = await parse_resume(state.files.resume_path)
        state.jd = await parse_job_description(state.files.jd_path)
        logger.info("Parser node completed for session %s", state.metadata.session_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Parser node failed: %s", exc)
        state.metadata.errors.append(f"parser_node_failed: {exc}")
    return state
