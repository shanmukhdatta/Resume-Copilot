"""Conditional routing logic for the LangGraph workflow."""
from app.config import get_settings
from app.schemas.state_schema import ResumeCopilotState


def route_after_validation(state: ResumeCopilotState) -> str:
    """Decide whether to proceed to rendering or retry failed agents."""
    settings = get_settings()
    if state.validation.overall_passed:
        return "rendering"
    if state.metadata.retry_count >= settings.MAX_VALIDATION_RETRIES:
        # Exhausted retries: proceed anyway rather than looping forever.
        return "rendering"
    return "retry"
