"""Jinja2-based template engine wrapper. Templates live under
app/templates/<name>/resume.html.j2 and can be extended without any
business-logic changes."""
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATE_ROOT = Path("app/templates")


def get_environment(template_name: str) -> Environment:
    template_dir = _TEMPLATE_ROOT / template_name
    if not template_dir.exists():
        template_dir = _TEMPLATE_ROOT / "ats"
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "j2"]),
    )


def render_template(template_name: str, context: dict) -> str:
    env = get_environment(template_name)
    template = env.get_template("resume.html.j2")
    return template.render(**context)
