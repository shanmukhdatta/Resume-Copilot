"""Service wrapper for fetching evaluation results of a completed
session."""
from app.schemas.evaluation_schema import EvaluationReport
from app.services.cache_service import get_session


class SessionNotFoundError(Exception):
    """Raised when a session_id has no cached state."""


def get_evaluation(session_id: str) -> EvaluationReport:
    state = get_session(session_id)
    if state is None:
        raise SessionNotFoundError(f"No session found for id: {session_id}")
    return state.evaluation
