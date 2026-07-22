"""Tests for the JSON extraction helper used by the LLM output parser."""
from app.utils.json_utils import extract_json_block


def test_extract_json_from_fenced_block():
    raw = '```json\n{"a": 1, "b": [1, 2]}\n```'
    result = extract_json_block(raw)
    assert result.strip().startswith("{")
    assert result.strip().endswith("}")


def test_extract_json_with_surrounding_prose():
    raw = 'Here is the output:\n{"a": 1}\nHope that helps!'
    result = extract_json_block(raw)
    assert result == '{"a": 1}'
