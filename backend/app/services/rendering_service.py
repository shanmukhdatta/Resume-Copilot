"""Service that renders a completed session's resume into the
requested export format on demand."""
import os

from app.renderers.docx_renderer import render_docx
from app.renderers.html_renderer import render_html
from app.renderers.pdf_renderer import render_pdf
from app.services.cache_service import get_session
from app.utils.constants import EXPORT_FORMATS


class SessionNotFoundError(Exception):
    """Raised when a session_id has no cached state."""


class UnsupportedExportFormatError(Exception):
    """Raised when an unsupported export_format is requested."""


def render_session(session_id: str, export_format: str, template: str) -> str:
    if export_format not in EXPORT_FORMATS:
        raise UnsupportedExportFormatError(f"Unsupported export format: {export_format}")

    state = get_session(session_id)
    if state is None:
        raise SessionNotFoundError(f"No session found for id: {session_id}")

    if export_format == "html":
        return render_html(state.final_resume, template, session_id)
    if export_format == "pdf":
        return render_pdf(state.final_resume, template, session_id)
    return render_docx(state.final_resume, session_id)
