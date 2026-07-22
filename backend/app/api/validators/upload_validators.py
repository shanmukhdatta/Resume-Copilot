"""Request-level validation helpers for the upload endpoints."""
from fastapi import UploadFile

from app.config import get_settings


async def read_and_validate_upload(file: UploadFile) -> bytes:
    settings = get_settings()
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise ValueError(f"File exceeds max size of {settings.MAX_UPLOAD_SIZE_MB}MB.")
    return content
