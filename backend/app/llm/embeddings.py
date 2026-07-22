"""Lightweight embedding/similarity helpers used by evaluation & matching.

Uses RapidFuzz token-set similarity rather than a heavy embedding model,
which keeps the service deployable on free-tier infrastructure.
"""
from rapidfuzz import fuzz


def text_similarity(a: str, b: str) -> float:
    """Return a 0-100 fuzzy similarity score between two strings."""
    if not a or not b:
        return 0.0
    return fuzz.token_set_ratio(a, b)


def keyword_overlap(keywords: list[str], text: str) -> list[str]:
    """Return the subset of keywords that fuzzy-match within the text."""
    text_lower = text.lower()
    matched = []
    for kw in keywords:
        if not kw:
            continue
        if fuzz.partial_ratio(kw.lower(), text_lower) >= 80:
            matched.append(kw)
    return matched
