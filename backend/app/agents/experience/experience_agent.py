"""Experience Agent -- rewrites experience bullets for ATS optimization
while preserving all factual details (company, title, dates)."""
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.agents.prompt_context import section_keywords
from app.schemas.resume_schema import ExperienceEntry
from app.utils.json_utils import dumps
from app.utils.helpers import fill_prompt


class _ExperienceOutput(BaseModel):
    experience: list[ExperienceEntry] = []


class ExperienceAgent(BaseAgent):
    name = "experience"
    prompt_path = "app/prompts/experience/experience_prompt.txt"
    output_schema = _ExperienceOutput

    def build_prompt(self, state) -> str:
        template = self.load_prompt()
        keywords = section_keywords(state, "experience")
        return fill_prompt(
            template,
            keywords=", ".join(keywords),
            ranked_experience=", ".join(state.planning.ranked_experience),
            resume_experience_json=dumps(
                [e.model_dump() for e in state.resume.experience]
            ),
            jd_json=dumps(state.jd.model_dump()),
        )

    def apply_output(self, state, parsed_output: _ExperienceOutput):
        state.generated_sections.experience = [
            e.model_dump() for e in parsed_output.experience
        ]
