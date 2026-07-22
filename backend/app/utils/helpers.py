"""Small reusable helper functions with no external side effects."""
import re
import uuid


def new_id(prefix: str = "") -> str:
    """Generate a short unique id, optionally prefixed."""
    raw = uuid.uuid4().hex[:12]
    return f"{prefix}_{raw}" if prefix else raw


def slugify(text: str) -> str:
    """Convert arbitrary text into a filesystem/url safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def truncate(text: str, length: int = 200) -> str:
    """Truncate text to a max length, appending an ellipsis if cut."""
    if len(text) <= length:
        return text
    return text[: length - 1].rstrip() + "…"


def fill_prompt(template: str, **kwargs) -> str:
    """Substitute only `{known_key}` placeholders in a prompt template,
    leaving any other brace content (e.g. literal JSON examples embedded
    in the prompt) completely untouched. This is deliberately NOT
    str.format(), which would choke on/corrupt literal '{' '}' in the
    JSON schema examples that every prompt file includes."""

    def _replace(match: "re.Match") -> str:
        key = match.group(1)
        return str(kwargs[key]) if key in kwargs else match.group(0)

    return re.sub(r"\{(\w+)\}", _replace, template)


def safe_get(d: dict, *keys, default=None):
    """Safely traverse nested dictionaries by a sequence of keys."""
    current = d
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
