"""File storage service used by the upload API routes."""
import os

from app.config import get_settings
from app.utils.file_utils import file_size_mb, get_extension, save_upload
from app.utils.helpers import new_id


class UnsupportedFileError(Exception):
    """Raised when an uploaded file's extension isn't supported."""


class FileTooLargeError(Exception):
    """Raised when an uploaded file exceeds the configured size limit."""


def store_upload(file_bytes: bytes, original_filename: str, subdir: str, allowed_extensions: set[str]) -> dict:
    settings = get_settings()
    ext = get_extension(original_filename)
    if ext not in allowed_extensions:
        raise UnsupportedFileError(f"Unsupported file extension: {ext}")

    file_id = new_id("file")
    safe_name = f"{file_id}{ext}"
    dest_dir = os.path.join(settings.UPLOAD_DIR, subdir)
    saved_path = save_upload(file_bytes, dest_dir, safe_name)

    size_mb = file_size_mb(saved_path)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        os.remove(saved_path)
        raise FileTooLargeError(
            f"File exceeds max size of {settings.MAX_UPLOAD_SIZE_MB}MB (was {size_mb:.2f}MB)."
        )

    return {"file_id": file_id, "filename": original_filename, "saved_path": saved_path, "size_mb": round(size_mb, 3)}
