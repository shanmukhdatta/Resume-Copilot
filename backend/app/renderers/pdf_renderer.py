"""Renders the final resume into a PDF using WeasyPrint. Falls back to
returning the HTML path (with a warning) if WeasyPrint or its native
dependencies (cairo/pango) aren't available in the environment."""
import os

from app.config import get_settings
from app.renderers.html_renderer import render_html
from app.schemas.resume_schema import GeneratedResume
from app.utils.file_utils import ensure_dir
from app.utils.logger import get_logger

logger = get_logger(__name__)


def render_pdf(resume: GeneratedResume, template_name: str, session_id: str) -> str:
    settings = get_settings()
    html_path = render_html(resume, template_name, session_id)

    try:
        from weasyprint import HTML

        out_dir = ensure_dir(settings.EXPORT_DIR)
        out_path = os.path.join(out_dir, f"{session_id}_resume.pdf")
        HTML(filename=html_path).write_pdf(out_path)
        return out_path
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "WeasyPrint unavailable (%s); returning HTML instead of PDF. "
            "Install system libs (cairo/pango) to enable PDF export.",
            exc,
        )
        return html_path
