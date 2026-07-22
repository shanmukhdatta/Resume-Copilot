"""Re-exports the shared LangGraph state type for convenient importing
within the graph package."""
from app.schemas.state_schema import ResumeCopilotState

__all__ = ["ResumeCopilotState"]
