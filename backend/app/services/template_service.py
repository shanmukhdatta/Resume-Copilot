"""Lists available resume templates for the /templates API route."""
import os

_TEMPLATE_ROOT = "app/templates"


def list_templates() -> list[str]:
    if not os.path.isdir(_TEMPLATE_ROOT):
        return []
    return sorted(
        name for name in os.listdir(_TEMPLATE_ROOT)
        if os.path.isfile(os.path.join(_TEMPLATE_ROOT, name, "resume.html.j2"))
    )
