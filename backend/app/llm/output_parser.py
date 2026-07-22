"""Parses raw LLM text output into validated Pydantic models."""
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.utils.json_utils import extract_json_block, loads
from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class OutputParsingError(Exception):
    """Raised when an LLM response cannot be parsed into the target schema."""


def parse_structured_output(raw_text: str, schema: type[T]) -> T:
    """Extract JSON from raw LLM text and validate it against a schema."""
    json_str = extract_json_block(raw_text)
    try:
        data = loads(json_str)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to parse JSON from LLM output: %s", exc)
        raise OutputParsingError(f"Invalid JSON from LLM: {exc}") from exc

    try:
        return schema.model_validate(data)
    except ValidationError as exc:
        logger.error("Schema validation failed: %s", exc)
        raise OutputParsingError(f"Schema validation failed: {exc}") from exc
