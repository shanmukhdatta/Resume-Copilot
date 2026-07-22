"""Resolves uploaded file_ids back to disk paths for the resume/JD
parsing stage."""
import glob
import os

from app.config import get_settings


def resolve_upload_path(file_id: str, subdir: str) -> str | None:
    settings = get_settings()
    pattern = os.path.join(settings.UPLOAD_DIR, subdir, f"{file_id}.*")
    matches = glob.glob(pattern)
    return matches[0] if matches else None
