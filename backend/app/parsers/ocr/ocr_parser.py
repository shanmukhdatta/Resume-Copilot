"""Standalone OCR utility for image-based resume/JD uploads (JPEG/PNG)."""
from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_image(path: str) -> str:
    """OCR an image file to plain text using pytesseract."""
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        logger.error("Pillow/pytesseract not installed; cannot OCR image.")
        return ""

    try:
        return pytesseract.image_to_string(Image.open(path))
    except Exception as exc:  # noqa: BLE001
        logger.error("OCR failed for %s: %s", path, exc)
        return ""
