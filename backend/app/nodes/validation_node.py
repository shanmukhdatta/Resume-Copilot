"""Validation Node -- runs all validators and decides pass/retry."""
from app.schemas.state_schema import ResumeCopilotState
from app.validators.ats_validator import validate_ats
from app.validators.consistency_validator import validate_consistency
from app.validators.duplicate_validator import validate_duplicates
from app.validators.grammar_validator import validate_grammar
from app.validators.hallucination_validator import validate_hallucination
from app.validators.schema_validator import validate_schema
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def validation_node(state: ResumeCopilotState) -> ResumeCopilotState:
    state.metadata.current_node = "validation"

    report = state.validation
    report.schema_valid, schema_issues = validate_schema(state.final_resume)
    report.ats_valid, ats_issues = validate_ats(state.final_resume, state.jd)
    report.grammar_valid, grammar_issues = validate_grammar(state.final_resume)
    report.hallucination_free, halluc_issues = await validate_hallucination(state)
    report.consistent, consistency_issues = validate_consistency(state.final_resume)
    report.duplicate_free, dup_issues = validate_duplicates(state.final_resume)

    all_issues = {
        "schema": schema_issues,
        "ats": ats_issues,
        "grammar": grammar_issues,
        "hallucination": halluc_issues,
        "consistency": consistency_issues,
        "duplicates": dup_issues,
    }

    failed_sections = [k for k, v in all_issues.items() if v]
    report.failed_sections = failed_sections
    report.overall_passed = len(failed_sections) == 0

    state.validation = report
    logger.info(
        "Validation node result for session %s: passed=%s issues=%s",
        state.metadata.session_id,
        report.overall_passed,
        failed_sections,
    )
    return state
