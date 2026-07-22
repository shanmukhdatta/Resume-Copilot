"""Optional persistence models for storing completed sessions. Only
used when DATABASE_URL is configured; the app fully functions in
stateless/in-memory mode otherwise."""
from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ResumeSession(Base):
    __tablename__ = "resume_sessions"

    session_id = Column(String, primary_key=True)
    resume_filename = Column(String)
    jd_filename = Column(String)
    final_resume_json = Column(Text)
    evaluation_json = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
