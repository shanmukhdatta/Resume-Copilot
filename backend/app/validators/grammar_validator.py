"""Grammar validation. Uses language-tool-python when available (as
specified in the architecture); otherwise falls back to a light
heuristic check so the pipeline keeps working on minimal-dependency
deployments (language-tool-python requires a local Java runtime)."""
from app.schemas.resume_schema import GeneratedResume
from app.utils.logger import get_logger

logger = get_logger(__name__)

_tool = None
_tool_load_attempted = False


def _get_tool():
    global _tool, _tool_load_attempted
    if _tool_load_attempted:
        return _tool
    _tool_load_attempted = True
    try:
        import language_tool_python

        _tool = language_tool_python.LanguageTool("en-US")
    except Exception as exc:  # noqa: BLE001
        logger.warning("language_tool_python unavailable, using heuristic grammar check: %s", exc)
        _tool = None
    return _tool


def _heuristic_check(text: str) -> list[str]:
    issues = []
    if "  " in text:
        issues.append("Double space detected.")
    if text and text[0].islower():
        issues.append("Sentence should start with a capital letter.")
    return issues


def validate_grammar(resume: GeneratedResume) -> tuple[bool, list[str]]:
    tool = _get_tool()
    issues: list[str] = []
    text = resume.summary

    if not text:
        return True, []

    if tool is not None:
        matches = tool.check(text)
        issues = [m.message for m in matches[:5]]
    else:
        issues = _heuristic_check(text)

    return len(issues) == 0, issues
