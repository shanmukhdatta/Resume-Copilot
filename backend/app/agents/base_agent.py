"""Base class shared by all generation agents.

Enforces the contract: an agent reads the shared state but writes ONLY to
its own designated output field. Prompt loading, LLM invocation, and
structured-output parsing are centralized here so individual agents stay
tiny and declarative.
"""
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel

from app.llm.llm_factory import get_llm_client
from app.llm.output_parser import parse_structured_output
from app.utils.logger import get_logger
from app.utils.timing import timed

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for a single-responsibility generation agent."""

    name: str = "base"
    prompt_path: str = ""
    output_schema: type[BaseModel]
    # Top-level ResumeCopilotState field this agent is allowed to write to.
    state_field: str = "generated_sections"

    def __init__(self):
        self.llm = get_llm_client()

    def load_prompt(self) -> str:
        """Load this agent's dedicated prompt template from disk."""
        path = Path(self.prompt_path)
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_path}")
        return path.read_text(encoding="utf-8")

    @abstractmethod
    def build_prompt(self, state) -> str:
        """Fill the loaded prompt template with values from shared state."""
        raise NotImplementedError

    @abstractmethod
    def apply_output(self, state, parsed_output: BaseModel):
        """Write this agent's parsed output into its own state field only."""
        raise NotImplementedError

    async def run(self, state):
        """Execute the agent: build prompt -> call LLM -> parse -> apply.

        Returns a PARTIAL update dict (only this agent's owned field plus
        metadata) rather than the full state object, so LangGraph's
        parallel fan-out doesn't see concurrent writes to unrelated
        channels in the same super-step.
        """
        with timed(f"agent:{self.name}"):
            try:
                prompt = self.build_prompt(state)
                raw_output = await self.llm.generate(prompt)
                parsed = parse_structured_output(raw_output, self.output_schema)
                self.apply_output(state, parsed)
                logger.info("Agent '%s' completed successfully.", self.name)
            except Exception as exc:  # noqa: BLE001
                logger.error("Agent '%s' failed: %s", self.name, exc)
                state.metadata.errors.append(f"{self.name}_agent_failed: {exc}")

        return {
            self.state_field: getattr(state, self.state_field),
            "metadata": state.metadata,
        }
