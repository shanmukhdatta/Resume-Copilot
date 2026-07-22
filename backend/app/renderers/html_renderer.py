"""Renders the final resume into a standalone HTML file."""
import os

from app.config import get_settings
from app.renderers.template_engine import render_template
from app.schemas.resume_schema import GeneratedResume
from app.utils.file_utils import ensure_dir


def render_html(resume: GeneratedResume, template_name: str, session_id: str) -> str:
    settings = get_settings()
    css_path = os.path.join("..", "..", "renderers", "css", f"{template_name}.css")

    html = render_template(
        template_name,
        {"resume": resume.model_dump(), "css_path": f"/static/css/{template_name}.css"},
    )

    out_dir = ensure_dir(settings.EXPORT_DIR)
    out_path = os.path.join(out_dir, f"{session_id}_resume.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
