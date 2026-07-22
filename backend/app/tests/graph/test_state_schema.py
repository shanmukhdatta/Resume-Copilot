"""Tests for the shared LangGraph state schema."""
from app.schemas.state_schema import ResumeCopilotState


def test_default_state_constructs():
    state = ResumeCopilotState()
    assert state.metadata.retry_count == 0
    assert state.generated_sections.summary == ""
    assert state.validation.overall_passed is True
