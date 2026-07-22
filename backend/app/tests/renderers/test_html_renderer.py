"""Smoke test for HTML rendering of a minimal resume."""
import os

from app.renderers.html_renderer import render_html
from app.schemas.resume_schema import ContactInfo, GeneratedResume


def test_render_html_creates_file(tmp_path, monkeypatch):
    monkeypatch.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    resume = GeneratedResume(contact=ContactInfo(full_name="Jane Doe", email="jane@example.com"), summary="A summary.")
    path = render_html(resume, "ats", "test-session")
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "Jane Doe" in content
