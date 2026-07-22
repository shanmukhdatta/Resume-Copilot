"""Verifies each generation agent writes only to its own designated
GeneratedSections field."""
import pytest

from app.agents.summary.summary_agent import SummaryAgent, _SummaryOutput
from app.schemas.state_schema import ResumeCopilotState


@pytest.mark.asyncio
async def test_summary_agent_applies_only_its_own_field():
    agent = SummaryAgent()
    state = ResumeCopilotState()
    agent.apply_output(state, _SummaryOutput(summary="Tailored summary text."))
    assert state.generated_sections.summary == "Tailored summary text."
    assert state.generated_sections.skills == []
