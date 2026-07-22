"""LLM Factory -- the ONLY place agents should obtain an LLM client from.

Agents must never instantiate a provider client directly; this keeps the
provider swappable (Gemini today, OpenAI/Anthropic tomorrow) with zero
changes to agent code.
"""
from functools import lru_cache

from app.config import get_settings
from app.llm.gemini import GeminiClient


class UnsupportedProviderError(Exception):
    """Raised when an unknown LLM_PROVIDER is configured."""


@lru_cache
def get_llm_client():
    """Return the configured LLM client singleton."""
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()

    if provider == "gemini":
        return GeminiClient()
    if provider == "openai":
        from app.llm.openai import OpenAIClient

        return OpenAIClient()
    if provider == "anthropic":
        from app.llm.anthropic import AnthropicClient

        return AnthropicClient()

    raise UnsupportedProviderError(f"Unsupported LLM provider: {provider}")
