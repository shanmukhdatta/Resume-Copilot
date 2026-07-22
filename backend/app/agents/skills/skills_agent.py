"""Skills Agent -- selects and categorizes verified skills."""
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.agents.prompt_context import section_keywords
from app.schemas.resume_schema import SkillCategory
from app.utils.json_utils import dumps
from app.utils.helpers import fill_prompt


class _SkillsOutput(BaseModel):
    skills: list[SkillCategory] = []


class SkillsAgent(BaseAgent):
    name = "skills"
    prompt_path = "app/prompts/skills/skills_prompt.txt"
    output_schema = _SkillsOutput

    def build_prompt(self, state) -> str:
        template = self.load_prompt()
        keywords = section_keywords(state, "skills")
        jd_skills = {
            "required_skills": state.jd.required_skills,
            "preferred_skills": state.jd.preferred_skills,
        }
        return fill_prompt(
            template,
            keywords=", ".join(keywords),
            resume_skills_json=dumps([s.model_dump() for s in state.resume.skills]),
            jd_skills_json=dumps(jd_skills),
        )

    def apply_output(self, state, parsed_output: _SkillsOutput):
        state.generated_sections.skills = [s.model_dump() for s in parsed_output.skills]
