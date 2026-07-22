"""Optional in-memory checkpoint store, allowing the workflow to be
resumed or inspected mid-run (e.g. for debugging retries)."""
from app.schemas.state_schema import ResumeCopilotState

_CHECKPOINTS: dict[str, ResumeCopilotState] = {}


def save_checkpoint(session_id: str, state: ResumeCopilotState) -> None:
    _CHECKPOINTS[session_id] = state


def load_checkpoint(session_id: str) -> ResumeCopilotState | None:
    return _CHECKPOINTS.get(session_id)
