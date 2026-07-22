"""Summary Agent -- generates the professional summary section."""
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.agents.prompt_context import section_keywords
from app.utils.json_utils import dumps
from app.utils.helpers import fill_prompt


class _SummaryOutput(BaseModel):
    summary: str = ""


class SummaryAgent(BaseAgent):
    name = "summary"
    prompt_path = "app/prompts/summary/summary_prompt.txt"
    output_schema = _SummaryOutput

    def build_prompt(self, state) -> str:
        template = self.load_prompt()
        keywords = section_keywords(state, "summary")
        return fill_prompt(
            template,
            detected_role=state.planning.detected_role,
            keywords=", ".join(keywords),
            resume_json=dumps(state.resume.model_dump()),
            jd_json=dumps(state.jd.model_dump()),
        )

    def apply_output(self, state, parsed_output: _SummaryOutput):
        state.generated_sections.summary = parsed_output.summary
