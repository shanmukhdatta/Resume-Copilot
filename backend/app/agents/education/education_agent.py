"""Education Agent -- formats education entries consistently, preserving
all factual details."""
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.schemas.resume_schema import EducationEntry
from app.utils.json_utils import dumps
from app.utils.helpers import fill_prompt


class _EducationOutput(BaseModel):
    education: list[EducationEntry] = []


class EducationAgent(BaseAgent):
    name = "education"
    prompt_path = "app/prompts/education/education_prompt.txt"
    output_schema = _EducationOutput

    def build_prompt(self, state) -> str:
        template = self.load_prompt()
        return fill_prompt(
            template,
            resume_education_json=dumps(
                [e.model_dump() for e in state.resume.education]
            )
        )

    def apply_output(self, state, parsed_output: _EducationOutput):
        state.generated_sections.education = [
            e.model_dump() for e in parsed_output.education
        ]
