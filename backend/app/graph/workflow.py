"""High-level workflow entry point used by the API/service layer to run
the full graph end-to-end for a given session."""
from app.graph.builder import build_graph
from app.schemas.state_schema import ResumeCopilotState
from app.utils.logger import get_logger
from app.utils.timing import timed

logger = get_logger(__name__)

_compiled_graph = None


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


async def run_resume_workflow(initial_state: ResumeCopilotState) -> ResumeCopilotState:
    """Execute the full LangGraph pipeline for one resume generation
    session and return the final populated state."""
    graph = get_compiled_graph()
    with timed(f"workflow:{initial_state.metadata.session_id}"):
        result = await graph.ainvoke(initial_state)
    # LangGraph returns a dict-like mapping of the state's fields; hydrate
    # it back into our strongly-typed model for consistent downstream use.
    if isinstance(result, ResumeCopilotState):
        return result
    return ResumeCopilotState.model_validate(result)
