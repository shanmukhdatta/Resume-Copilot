# AI Resume Copilot — Backend

Production-oriented AI Resume Copilot backend. FastAPI + LangGraph
multi-agent orchestration engine that parses a resume and job
description, plans a tailoring strategy, runs 8 parallel generation
agents, validates and assembles a final resume, renders it to
HTML/PDF/DOCX, and produces ATS scoring + recommendations.

Backend only — no frontend is included.

## Architecture

```
Input -> Document Processing -> Structured State -> Planning
      -> Parallel Multi-Agent Generation -> Assembly -> Validation
      -> Rendering -> Evaluation -> Output
```

Implemented as a LangGraph `StateGraph` (`app/graph/builder.py`):

```
START -> upload -> parser -> planner
      -> [summary, skills, experience, projects, education,
          certifications, achievements, links]  (parallel fan-out)
      -> assembly -> validation
           -> (pass)  -> rendering -> evaluation -> END
           -> (fail)  -> retry (only failed sections) -> validation
```

See `app/` for the full modular folder structure (api, graph, nodes,
agents, parsers, prompts, llm, schemas, services, renderers,
templates, validators, evaluation, utils, database, tests) — it
mirrors the architecture 1:1, with a single responsibility per module.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then set GEMINI_API_KEY
```

Notes on optional system dependencies:
- **WeasyPrint** (PDF export) needs native Cairo/Pango libraries.
  On Debian/Ubuntu: `apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0`.
  If unavailable, PDF export automatically falls back to HTML.
- **language-tool-python** (grammar validation) needs a local Java
  runtime on first run (it downloads LanguageTool). If Java isn't
  available, the grammar validator automatically falls back to a
  lightweight heuristic check — the pipeline still runs end to end.
- **pytesseract** (OCR fallback for scanned PDFs) needs the
  `tesseract-ocr` system binary.

None of these are required to run the API and the core text-based
pipeline; they only affect PDF export, grammar validation depth, and
scanned-PDF OCR respectively, and every code path degrades gracefully
without them.

## Running

```bash
uvicorn app.main:app --reload --port 8000
```

- Interactive API docs: http://localhost:8000/docs
- Health check: `GET /api/v1/health`

## API Flow

1. `POST /api/v1/upload/resume` (multipart file) → `{file_id, ...}`
2. `POST /api/v1/upload/jd` (multipart file) → `{file_id, ...}`
3. `POST /api/v1/resume/generate`
   `{"resume_file_id": "...", "jd_file_id": "...", "user_notes": "", "template": "ats"}`
   → runs the full LangGraph pipeline, returns the final resume,
   validation report, and evaluation report.
4. `POST /api/v1/evaluation` `{"session_id": "..."}` → re-fetch the
   evaluation report for a completed session.
5. `GET /api/v1/templates` → list available templates.
6. `POST /api/v1/templates/render`
   `{"session_id": "...", "export_format": "pdf|docx|html", "template": "ats"}`
   → renders/exports the resume, returns the file path.
7. `GET /api/v1/templates/download/{session_id}/{export_format}` →
   downloads the rendered file directly.

## LLM Provider

All agents call the LLM exclusively through `app/llm/llm_factory.py`.
Provider is selected via `LLM_PROVIDER` in `.env` (`gemini` by
default; `openai` and `anthropic` implementations are included behind
the same interface). If no API key is configured, the client runs in
a deterministic stub mode so the graph, validators, and rendering
pipeline remain fully testable offline.

## Testing

```bash
pytest app/tests -v
```

## Deployment (free-tier target)

- Backend: Render (Docker or native Python web service)
- AI: Google Gemini free tier
- Database (optional): Supabase PostgreSQL — set `DATABASE_URL`
- Frontend (separate repo): Vercel

## Docker

```bash
docker-compose up --build
```

## Key Design Decisions

- **Strict separation of concerns**: parsing, planning, generation,
  assembly, validation, rendering, and evaluation are distinct graph
  nodes/modules; no module has more than one responsibility.
- **No hallucination by construction**: every generation prompt
  instructs the model to use only parsed source data, and the
  validation layer runs an additional LLM fact-check pass plus a
  fuzzy-match cross-check on the experience/skills sections.
  Validation failures trigger a retry of only the implicated
  section(s), never a full regeneration.
- **Swappable LLM provider**: agents never import a provider SDK
  directly; everything goes through `llm_factory.py`.
- **Strongly typed shared state**: the entire LangGraph state is a
  Pydantic model tree (`app/schemas/state_schema.py`) — no raw dicts
  with unknown shape flow through the graph.
