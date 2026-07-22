"""Planner Node -- runs the Planning Agent to produce a generation
strategy from the parsed resume + JD."""
from app.agents.planner.planner_agent import PlannerAgent
from app.schemas.state_schema import ResumeCopilotState

_planner = PlannerAgent()


async def planner_node(state: ResumeCopilotState) -> ResumeCopilotState:
    state.metadata.current_node = "planner"
    return await _planner.run(state)
