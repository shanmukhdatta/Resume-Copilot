"""DOCX text extraction using python-docx."""
from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_docx(path: str) -> str:
    """Extract raw text (paragraphs + tables) from a .docx file."""
    try:
        import docx
    except ImportError:
        logger.error("python-docx not installed; cannot parse DOCX.")
        return ""

    document = docx.Document(path)
    chunks: list[str] = [p.text for p in document.paragraphs if p.text.strip()]

    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells)
            if row_text.strip(" |"):
                chunks.append(row_text)

    return "\n".join(chunks)
