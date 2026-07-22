"""Rendering Node -- renders the final resume into HTML (and optionally
PDF/DOCX) using the configured template."""
from app.renderers.html_renderer import render_html
from app.schemas.state_schema import ResumeCopilotState
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def rendering_node(state: ResumeCopilotState) -> ResumeCopilotState:
    state.metadata.current_node = "rendering"
    try:
        html_path = render_html(state.final_resume, state.metadata.template, state.metadata.session_id)
        state.rendered_paths["html"] = html_path
        logger.info("Rendering node produced HTML for session %s", state.metadata.session_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Rendering node failed: %s", exc)
        state.metadata.errors.append(f"rendering_node_failed: {exc}")
    return state
