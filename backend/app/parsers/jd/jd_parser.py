"""Job description parsing: extracts raw text then structures it via LLM."""
import os

from app.llm.llm_factory import get_llm_client
from app.llm.output_parser import parse_structured_output
from app.parsers.docx.docx_parser import extract_text_from_docx
from app.parsers.pdf.pdf_parser import extract_text_from_pdf
from app.schemas.jd_schema import ParsedJobDescription
from app.utils.helpers import fill_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)

JD_STRUCTURING_PROMPT = """You convert raw job description text into structured JSON.
Return ONLY valid JSON matching this shape, no prose, no markdown fences:
{
  "title": "", "company": "", "location": "", "seniority": "",
  "required_skills": [], "preferred_skills": [],
  "responsibilities": [], "qualifications": [], "keywords": []
}

Rules:
- Use only information present in the text below. Never invent details.
- keywords should be the most important ATS-relevant terms (skills, tools, role terms).

JOB DESCRIPTION TEXT:
{text}
"""


def extract_raw_text(path: str) -> str:
    """Extract raw text from a JD file (PDF, DOCX, or plain text)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    if ext == ".docx":
        return extract_text_from_docx(path)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


async def parse_job_description(path: str) -> ParsedJobDescription:
    """Parse a JD file into a structured ParsedJobDescription."""
    raw_text = extract_raw_text(path)
    if not raw_text.strip():
        logger.warning("No text extracted from JD file: %s", path)
        return ParsedJobDescription(raw_text="")

    client = get_llm_client()
    response = await client.generate(fill_prompt(JD_STRUCTURING_PROMPT, text=raw_text[:12000]))

    try:
        parsed = parse_structured_output(response, ParsedJobDescription)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falling back to raw-text-only JD parse: %s", exc)
        parsed = ParsedJobDescription()

    parsed.raw_text = raw_text
    return parsed
