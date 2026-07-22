"""Validates the final resume against its Pydantic schema."""
from app.schemas.resume_schema import GeneratedResume


def validate_schema(resume: GeneratedResume) -> tuple[bool, list[str]]:
    """Re-validate the resume model; returns (passed, issues)."""
    try:
        GeneratedResume.model_validate(resume.model_dump())
        return True, []
    except Exception as exc:  # noqa: BLE001
        return False, [str(exc)]
