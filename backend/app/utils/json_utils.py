"""JSON serialization helpers backed by orjson for speed, with a
stdlib-json fallback so the module still works if orjson isn't installed."""
import json as _json

try:
    import orjson

    def dumps(obj) -> str:
        """Serialize an object to a JSON string."""
        return orjson.dumps(obj).decode("utf-8")

    def loads(raw):
        """Deserialize a JSON string/bytes into a Python object."""
        return orjson.loads(raw)

except ImportError:  # pragma: no cover - fallback path

    def dumps(obj) -> str:
        return _json.dumps(obj, default=str)

    def loads(raw):
        return _json.loads(raw)


def extract_json_block(text: str) -> str:
    """Extract the first JSON object/array substring from an LLM response
    that may contain markdown fences or extra prose around the JSON."""
    text = text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    start_candidates = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if not start_candidates:
        return text
    start = min(start_candidates)
    end_brace = text.rfind("}")
    end_bracket = text.rfind("]")
    end = max(end_brace, end_bracket)
    if end == -1 or end < start:
        return text
    return text[start : end + 1]
