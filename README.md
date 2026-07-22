# AI Resume Copilot

A resume-tailoring product with two parts, shipped together:

```
resume-copilot/
├── backend/        FastAPI + LangGraph multi-agent pipeline (see backend/README.md)
├── frontend/        static HTML/CSS/JS UI, no build step (see frontend/README.md)
├── screenshots/      real Chromium screenshots of the frontend
├── ARCHITECTURE.md    project structure, folder structure, and the verified LangGraph workflow
└── AUDIT_REPORT.md   structural/reusability audit of the backend
```

## Quick start

```bash
# 1. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000

# 2. Frontend (separate terminal)
cd frontend
python3 -m http.server 5500
```

Open `http://localhost:5500`. Upload a resume + job description, and it
runs the full 8-agent LangGraph pipeline against your own backend.

## What's in each screenshot

| File | Shows |
|---|---|
| `01-hero.png` | Landing hero — headline, CTA, animated "tailoring" resume card |
| `02-how-it-works-and-demo-intro.png` | The 3-step process cards + demo section intro |
| `03-demo-upload-panel.png` | Resume/JD dropzones, notes field, template picker |
| `04-agents-generating.png` | Live progress grid while the 8 agents run |
| `05-results-and-score.png` | ATS score ring, matched/missing skills, tailored resume preview |
| `06-agents-grid-and-faq.png` | The "eight agents, one job each" section + FAQ |

Screenshots were taken with real headless Chromium (Playwright), not an
approximation — what you see is what actually renders.

## Design system

Apple-inflected by request: native system font stack (renders as real
SF Pro on Apple devices, no webfont CDN needed), off-white/near-black
palette with a single blue accent, generous whitespace, soft shadows,
and a signature hero element — a resume card that visibly "tailors"
itself with a sweeping highlight animation — instead of stock photography.
Full token list is at the top of `frontend/css/style.css`.

## Where things stand / what's next

The backend architecture, LangGraph workflow, and validation pipeline
are fully implemented and tested — see `ARCHITECTURE.md` for the
verified project/folder structure and the exact graph topology, and
`AUDIT_REPORT.md` for the reusability audit. The frontend talks to the
real API end-to-end, including:

- **ATS score, keyword coverage, resume match** — score ring + metrics.
- **Recommendations and "what to improve"** — previously computed by
  the backend but silently dropped by the frontend; now rendered.
- **Skill-gap learning resources** — for each missing skill, the
  backend (`app/evaluation/learning_resources.py`) suggests a real,
  stable link: an official-docs page for common skills (Python,
  Kubernetes, Terraform, etc.) from a small curated table, or a real
  search-results URL on Coursera/freeCodeCamp as a fallback for
  anything not in that table. Deliberately does NOT ask an LLM to
  invent specific course names or URLs, since a hallucinated course
  link is worse than no suggestion.

The one thing neither half can prove in this sandbox is generation
*quality*, since no `GEMINI_API_KEY` is configured here — the agents
run in a deterministic stub mode. Wire in a real key and the tailored
content, ATS score, and resume preview will populate with real output
instead of empty placeholders.

Forward-looking ideas are tracked as comments directly in the code
(see the header comment in `frontend/index.html` and the "FUTURE"
notes throughout `frontend/js/`), rather than a separate roadmap file
that inevitably drifts out of sync with the code.
