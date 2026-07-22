"""Factory that dispatches document parsing based on file type."""
import os

from app.llm.llm_factory import get_llm_client
from app.llm.output_parser import parse_structured_output
from app.parsers.docx.docx_parser import extract_text_from_docx
from app.parsers.pdf.pdf_parser import extract_text_from_pdf
from app.schemas.resume_schema import ParsedResume
from app.utils.constants import SUPPORTED_RESUME_EXTENSIONS
from app.utils.helpers import fill_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)

RESUME_STRUCTURING_PROMPT = """You convert raw resume text into structured JSON.
Return ONLY valid JSON matching this exact shape, no prose, no markdown fences:
{
  "contact": {"full_name": "", "email": "", "phone": "", "location": "",
               "links": [{"label": "", "url": ""}]},
  "summary": "",
  "skills": [{"category": "", "skills": []}],
  "experience": [{"company": "", "title": "", "location": "",
                    "start_date": "", "end_date": "", "bullets": []}],
  "projects": [{"name": "", "description": "", "technologies": [],
                  "bullets": [], "link": ""}],
  "education": [{"institution": "", "degree": "", "field_of_study": "",
                   "start_date": "", "end_date": "", "gpa": "", "details": []}],
  "certifications": [{"name": "", "issuer": "", "date": ""}],
  "achievements": [{"title": "", "description": "", "date": ""}]
}

CRITICAL RULES:
- Use ONLY information explicitly present in the resume text below.
- Never invent companies, dates, skills, achievements, or certifications.
- If a field is missing, leave it as an empty string or empty list.

RESUME TEXT:
{text}
"""


class UnsupportedFileTypeError(Exception):
    """Raised when a file extension is not supported by any parser."""


def extract_raw_text(path: str) -> str:
    """Route a resume file to the correct raw-text extractor."""
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_RESUME_EXTENSIONS:
        raise UnsupportedFileTypeError(f"Unsupported resume file type: {ext}")
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    return extract_text_from_docx(path)


async def parse_resume(path: str) -> ParsedResume:
    """Parse a resume file into a structured ParsedResume via the LLM."""
    raw_text = extract_raw_text(path)
    if not raw_text.strip():
        logger.warning("No text extracted from resume file: %s", path)
        return ParsedResume(raw_text="")

    client = get_llm_client()
    response = await client.generate(
        fill_prompt(RESUME_STRUCTURING_PROMPT, text=raw_text[:16000])
    )

    try:
        parsed = parse_structured_output(response, ParsedResume)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falling back to raw-text-only resume parse: %s", exc)
        parsed = ParsedResume()

    parsed.raw_text = raw_text
    return parsed
