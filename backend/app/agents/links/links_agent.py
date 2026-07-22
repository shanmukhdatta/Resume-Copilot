"""Links Agent -- formats candidate links (GitHub, LinkedIn, portfolio)
consistently."""
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent
from app.schemas.resume_schema import ContactLink
from app.utils.json_utils import dumps
from app.utils.helpers import fill_prompt


class _LinksOutput(BaseModel):
    links: list[ContactLink] = []


class LinksAgent(BaseAgent):
    name = "links"
    prompt_path = "app/prompts/links/links_prompt.txt"
    output_schema = _LinksOutput

    def build_prompt(self, state) -> str:
        template = self.load_prompt()
        return fill_prompt(
            template,
            resume_links_json=dumps(
                {
                    "links": [l.model_dump() for l in state.resume.contact.links],
                    "email": state.resume.contact.email,
                }
            )
        )

    def apply_output(self, state, parsed_output: _LinksOutput):
        state.generated_sections.links = [l.model_dump() for l in parsed_output.links]
