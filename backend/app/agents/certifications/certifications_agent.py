"""Certifications Agent -- includes only certifications explicitly
present in the source resume."""
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.schemas.resume_schema import CertificationEntry
from app.utils.json_utils import dumps
from app.utils.helpers import fill_prompt


class _CertificationsOutput(BaseModel):
    certifications: list[CertificationEntry] = []


class CertificationsAgent(BaseAgent):
    name = "certifications"
    prompt_path = "app/prompts/certifications/certifications_prompt.txt"
    output_schema = _CertificationsOutput

    def build_prompt(self, state) -> str:
        template = self.load_prompt()
        return fill_prompt(
            template,
            resume_certifications_json=dumps(
                [c.model_dump() for c in state.resume.certifications]
            )
        )

    def apply_output(self, state, parsed_output: _CertificationsOutput):
        state.generated_sections.certifications = [
            c.model_dump() for c in parsed_output.certifications
        ]
