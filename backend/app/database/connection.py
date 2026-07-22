"""Optional database connection (Supabase PostgreSQL / any SQLAlchemy
compatible DB). Only activates if DATABASE_URL is configured."""
from app.config import get_settings

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        if not settings.DATABASE_URL:
            return None
        from sqlalchemy import create_engine

        _engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        if engine is None:
            return None
        from sqlalchemy.orm import sessionmaker

        _SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return _SessionLocal
