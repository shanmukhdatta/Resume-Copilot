"""Shared helpers for building agent prompts from the Planning Agent's
output. Centralized here so every generation agent reuses the same
logic instead of each re-implementing its own copy (DRY)."""


def section_keywords(state, section_name: str) -> list[str]:
    """Return the keywords the Planner flagged for a given section,
    falling back to the overall ATS keyword list if the planner didn't
    produce a specific plan for that section."""
    for plan in state.planning.section_plans:
        if plan.section == section_name:
            return plan.keywords_to_emphasize
    return state.planning.ats_keywords
