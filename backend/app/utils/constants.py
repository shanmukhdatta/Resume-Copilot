"""Centralized constants used across the application."""

SUPPORTED_RESUME_EXTENSIONS = {".pdf", ".docx"}
SUPPORTED_JD_EXTENSIONS = {".pdf", ".txt", ".docx"}

AGENT_NAMES = [
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
    "achievements",
    "links",
]

RESUME_SECTIONS = AGENT_NAMES

VALIDATION_STATUS_PASS = "pass"
VALIDATION_STATUS_FAIL = "fail"

EXPORT_FORMATS = {"pdf", "docx", "html"}

DEFAULT_TEMPLATE = "ats"
