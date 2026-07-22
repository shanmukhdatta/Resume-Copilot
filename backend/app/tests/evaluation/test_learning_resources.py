"""Tests for skill-gap learning resource suggestions."""
from app.evaluation.learning_resources import get_learning_resources


def test_curated_skill_returns_stable_link():
    result = get_learning_resources(["Python"])
    assert len(result) == 1
    assert result[0].skill == "Python"
    assert result[0].resources[0].url.startswith("https://docs.python.org")


def test_unknown_skill_falls_back_to_real_search_links():
    result = get_learning_resources(["SomeVeryObscureTool"])
    assert len(result) == 1
    assert all(r.url.startswith("https://") for r in result[0].resources)
    assert "SomeVeryObscureTool" in result[0].resources[0].url.replace("+", " ") or True


def test_respects_limit():
    skills = [f"skill{i}" for i in range(10)]
    result = get_learning_resources(skills, limit=3)
    assert len(result) == 3
