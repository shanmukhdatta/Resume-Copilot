"""Projects Agent -- selects, ranks, and polishes project entries."""
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.agents.prompt_context import section_keywords
from app.schemas.resume_schema import ProjectEntry
from app.utils.json_utils import dumps
from app.utils.helpers import fill_prompt


class _ProjectsOutput(BaseModel):
    projects: list[ProjectEntry] = []


class ProjectsAgent(BaseAgent):
    name = "projects"
    prompt_path = "app/prompts/projects/projects_prompt.txt"
    output_schema = _ProjectsOutput

    def build_prompt(self, state) -> str:
        template = self.load_prompt()
        keywords = section_keywords(state, "projects")
        return fill_prompt(
            template,
            keywords=", ".join(keywords),
            ranked_projects=", ".join(state.planning.ranked_projects),
            resume_projects_json=dumps([p.model_dump() for p in state.resume.projects]),
            jd_json=dumps(state.jd.model_dump()),
        )

    def apply_output(self, state, parsed_output: _ProjectsOutput):
        state.generated_sections.projects = [
            p.model_dump() for p in parsed_output.projects
        ]
