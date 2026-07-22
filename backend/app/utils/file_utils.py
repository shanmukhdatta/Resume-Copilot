"""Filesystem helper utilities for reading/writing project artifacts."""
import os
import shutil
from pathlib import Path


def ensure_dir(path: str) -> str:
    """Ensure a directory exists and return its path."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def save_upload(file_bytes: bytes, dest_dir: str, filename: str) -> str:
    """Persist uploaded bytes to disk and return the saved path."""
    ensure_dir(dest_dir)
    dest_path = os.path.join(dest_dir, filename)
    with open(dest_path, "wb") as f:
        f.write(file_bytes)
    return dest_path


def get_extension(filename: str) -> str:
    """Return the lowercase file extension including the leading dot."""
    return os.path.splitext(filename)[1].lower()


def file_size_mb(path: str) -> float:
    """Return file size in megabytes."""
    return os.path.getsize(path) / (1024 * 1024)


def clear_dir(path: str) -> None:
    """Remove and recreate a directory (used mainly by tests)."""
    if os.path.exists(path):
        shutil.rmtree(path)
    ensure_dir(path)
