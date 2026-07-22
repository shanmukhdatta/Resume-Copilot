"""PDF text extraction using PyMuPDF, with an OCR fallback for scanned
(image-only) resumes."""
from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(path: str) -> str:
    """Extract raw text from a PDF file. Falls back to OCR when a page
    contains no extractable text layer (i.e. it is a scanned image)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF not installed; cannot parse PDF.")
        return ""

    text_chunks: list[str] = []
    doc = fitz.open(path)
    try:
        for page_index, page in enumerate(doc):
            page_text = page.get_text().strip()
            if not page_text:
                page_text = _ocr_page(page, page_index)
            text_chunks.append(page_text)
    finally:
        doc.close()

    return "\n".join(text_chunks)


def _ocr_page(page, page_index: int) -> str:
    """OCR a single scanned PDF page via pytesseract, best-effort."""
    try:
        from PIL import Image
        import pytesseract
        import io

        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img)
    except Exception as exc:  # noqa: BLE001
        logger.warning("OCR fallback failed for page %s: %s", page_index, exc)
        return ""
