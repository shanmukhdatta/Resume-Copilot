"""Planning Agent -- produces a resume generation strategy only.
Never generates resume content."""
from app.agents.base_agent import BaseAgent
from app.schemas.planning_schema import PlanningOutput
from app.utils.json_utils import dumps
from app.utils.helpers import fill_prompt


class PlannerAgent(BaseAgent):
    name = "planner"
    prompt_path = "app/prompts/planner/planner_prompt.txt"
    output_schema = PlanningOutput
    state_field = "planning"

    def build_prompt(self, state) -> str:
        template = self.load_prompt()
        return fill_prompt(
            template,
            resume_json=dumps(state.resume.model_dump()),
            jd_json=dumps(state.jd.model_dump()),
            user_notes=state.user_notes or "(none)",
        )

    def apply_output(self, state, parsed_output: PlanningOutput):
        state.planning = parsed_output
