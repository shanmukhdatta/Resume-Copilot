"""Achievements Agent -- rewrites achievements for clarity without
inventing awards or rankings."""
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.schemas.resume_schema import AchievementEntry
from app.utils.json_utils import dumps
from app.utils.helpers import fill_prompt


class _AchievementsOutput(BaseModel):
    achievements: list[AchievementEntry] = []


class AchievementsAgent(BaseAgent):
    name = "achievements"
    prompt_path = "app/prompts/achievements/achievements_prompt.txt"
    output_schema = _AchievementsOutput

    def build_prompt(self, state) -> str:
        template = self.load_prompt()
        return fill_prompt(
            template,
            resume_achievements_json=dumps(
                [a.model_dump() for a in state.resume.achievements]
            )
        )

    def apply_output(self, state, parsed_output: _AchievementsOutput):
        state.generated_sections.achievements = [
            a.model_dump() for a in parsed_output.achievements
        ]
