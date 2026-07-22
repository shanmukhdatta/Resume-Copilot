"""Shared FastAPI dependency providers."""
from app.config import Settings, get_settings


def settings_dependency() -> Settings:
    """FastAPI dependency that yields the cached Settings instance."""
    return get_settings()
