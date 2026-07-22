"""Simple in-memory cache for completed generation sessions, so the
evaluation/render endpoints can be called independently after
generation without recomputation."""
from app.schemas.state_schema import ResumeCopilotState

_SESSION_CACHE: dict[str, ResumeCopilotState] = {}


def cache_session(session_id: str, state: ResumeCopilotState) -> None:
    _SESSION_CACHE[session_id] = state


def get_session(session_id: str) -> ResumeCopilotState | None:
    return _SESSION_CACHE.get(session_id)
