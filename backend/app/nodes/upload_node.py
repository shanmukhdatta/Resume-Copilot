"""Upload Node -- first node in the graph; validates that referenced
uploaded files exist and records their metadata into shared state."""
import os

from app.schemas.state_schema import ResumeCopilotState
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def upload_node(state: ResumeCopilotState) -> ResumeCopilotState:
    state.metadata.current_node = "upload"
    for label, path in (
        ("resume", state.files.resume_path),
        ("jd", state.files.jd_path),
    ):
        if not path or not os.path.exists(path):
            msg = f"Missing or invalid {label} file path: {path}"
            logger.error(msg)
            state.metadata.errors.append(msg)
    logger.info("Upload node validated files for session %s", state.metadata.session_id)
    return state
