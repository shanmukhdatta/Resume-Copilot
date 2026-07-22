"""Maps missing skills to concrete learning resources.

Deliberately does NOT ask an LLM to invent course names or URLs for
this — a hallucinated course link is worse than no suggestion at all.
Instead: a small curated table of stable, official-docs-style links for
common skills, with a safe fallback to real (non-fabricated) search
URLs on reputable platforms for anything not in the table. Every URL
here is a real, standing page/search endpoint, not a specific course
that could go stale or never have existed.
"""
from urllib.parse import quote_plus

from pydantic import BaseModel, Field


class LearningResource(BaseModel):
    title: str
    provider: str
    url: str


class SkillResourceSuggestion(BaseModel):
    skill: str
    resources: list[LearningResource] = Field(default_factory=list)


# Curated, stable landing pages for the most common role/skill keywords.
# Add to this table over time rather than routing everything through the
# generic search fallback below.
_CURATED_RESOURCES: dict[str, list[LearningResource]] = {
    "python": [
        LearningResource(title="The Python Tutorial", provider="python.org", url="https://docs.python.org/3/tutorial/"),
    ],
    "fastapi": [
        LearningResource(title="FastAPI Documentation", provider="fastapi.tiangolo.com", url="https://fastapi.tiangolo.com/tutorial/"),
    ],
    "django": [
        LearningResource(title="Django Getting Started", provider="djangoproject.com", url="https://docs.djangoproject.com/en/stable/intro/tutorial01/"),
    ],
    "docker": [
        LearningResource(title="Docker Get Started Guide", provider="docker.com", url="https://docs.docker.com/get-started/"),
    ],
    "kubernetes": [
        LearningResource(title="Kubernetes Basics", provider="kubernetes.io", url="https://kubernetes.io/docs/tutorials/kubernetes-basics/"),
    ],
    "postgresql": [
        LearningResource(title="PostgreSQL Tutorial", provider="postgresql.org", url="https://www.postgresql.org/docs/current/tutorial.html"),
    ],
    "sql": [
        LearningResource(title="SQL course", provider="freeCodeCamp", url="https://www.freecodecamp.org/learn/relational-database/"),
    ],
    "react": [
        LearningResource(title="React Quick Start", provider="react.dev", url="https://react.dev/learn"),
    ],
    "aws": [
        LearningResource(title="AWS Skill Builder", provider="aws.amazon.com", url="https://skillbuilder.aws/"),
    ],
    "redis": [
        LearningResource(title="Redis Documentation", provider="redis.io", url="https://redis.io/docs/latest/"),
    ],
    "git": [
        LearningResource(title="Git Handbook", provider="git-scm.com", url="https://git-scm.com/doc"),
    ],
    "graphql": [
        LearningResource(title="GraphQL Learn", provider="graphql.org", url="https://graphql.org/learn/"),
    ],
    "terraform": [
        LearningResource(title="Terraform Get Started", provider="developer.hashicorp.com", url="https://developer.hashicorp.com/terraform/tutorials"),
    ],
    "typescript": [
        LearningResource(title="TypeScript Handbook", provider="typescriptlang.org", url="https://www.typescriptlang.org/docs/handbook/intro.html"),
    ],
}


def _search_fallback(skill: str) -> list[LearningResource]:
    """Real, always-valid search URLs (not a fabricated specific course)
    for any skill not present in the curated table above."""
    query = quote_plus(skill)
    return [
        LearningResource(
            title=f"\"{skill}\" courses on Coursera",
            provider="Coursera",
            url=f"https://www.coursera.org/search?query={query}",
        ),
        LearningResource(
            title=f"\"{skill}\" on freeCodeCamp News",
            provider="freeCodeCamp",
            url=f"https://www.freecodecamp.org/news/search/?query={query}",
        ),
    ]


def get_learning_resources(missing_skills: list[str], limit: int = 6) -> list[SkillResourceSuggestion]:
    """Return resource suggestions for each missing skill, capped at
    `limit` skills so the response stays a manageable size."""
    suggestions: list[SkillResourceSuggestion] = []
    for skill in missing_skills[:limit]:
        key = skill.strip().lower()
        resources = _CURATED_RESOURCES.get(key) or _search_fallback(skill)
        suggestions.append(SkillResourceSuggestion(skill=skill, resources=resources))
    return suggestions
