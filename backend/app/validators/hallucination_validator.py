"""Detects content in the generated resume unsupported by the original
parsed data, using an LLM fact-checking pass on the highest-risk section
(experience) plus a fast fuzzy-match cross-check on skills."""
from pathlib import Path

from rapidfuzz import fuzz

from app.llm.llm_factory import get_llm_client
from app.llm.output_parser import parse_structured_output
from app.schemas.state_schema import ResumeCopilotState
from app.utils.json_utils import dumps
from app.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)

_PROMPT_PATH = "app/prompts/validation/hallucination_prompt.txt"


class _HallucinationOutput(BaseModel):
    hallucinations: list[str] = []


def _skill_names(skills) -> set[str]:
    names = set()
    for cat in skills:
        entries = cat.get("skills", []) if isinstance(cat, dict) else getattr(cat, "skills", [])
        names.update(s.lower() for s in entries)
    return names


async def validate_hallucination(state: ResumeCopilotState) -> tuple[bool, list[str]]:
    issues: list[str] = []

    # Fast heuristic check: any generated skill not fuzzy-present in resume skills
    original_skills = _skill_names([s.model_dump() for s in state.resume.skills])
    generated_skills = _skill_names(state.final_resume.skills)
    for skill in generated_skills:
        if not any(fuzz.ratio(skill, orig) > 85 for orig in original_skills):
            issues.append(f"Unverified skill introduced: {skill}")

    # LLM fact-check pass on the experience section (highest fabrication risk)
    try:
        template = Path(_PROMPT_PATH).read_text(encoding="utf-8")
        generated_experience = [
            e.model_dump() if hasattr(e, "model_dump") else e
            for e in state.final_resume.experience
        ]
        prompt = template.format(
            original_json=dumps([e.model_dump() for e in state.resume.experience]),
            section_name="experience",
            generated_json=dumps(generated_experience),
        )
        client = get_llm_client()
        raw = await client.generate(prompt)
        parsed = parse_structured_output(raw, _HallucinationOutput)
        issues.extend(parsed.hallucinations)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Hallucination LLM check skipped due to error: %s", exc)

    return len(issues) == 0, issues
