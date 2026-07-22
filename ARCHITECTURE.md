# Architecture

This document describes how the system is put together: the full-stack
project layout, the backend's internal folder structure, and the exact
LangGraph workflow as it actually compiles and runs (not just as
originally specified — the topology below was extracted directly from
`build_graph().get_graph()` at verification time, not hand-drawn).

---

## 1. Full-stack project layout

```
resume-copilot/
├── backend/          FastAPI + LangGraph multi-agent pipeline
├── frontend/          static HTML/CSS/JS UI (no build step)
├── screenshots/        real Chromium captures of the frontend
├── README.md            quick start for the whole project
├── ARCHITECTURE.md      this file
└── AUDIT_REPORT.md      structural/reusability audit of the backend
```

The backend is the only piece that needs a server. The frontend is
static and can be hosted anywhere that serves files.

---

## 2. Backend folder structure

```
backend/app/
├── main.py, config.py, dependencies.py     entry point + centralized settings
│
├── api/
│   ├── routes/           upload.py, resume.py, evaluation.py, templates.py, health.py
│   ├── middleware/        request logging
│   ├── validators/        request-level validation (upload size/type)
│   └── exceptions/        centralized FastAPI exception handlers
│
├── graph/
│   ├── builder.py         constructs & compiles the LangGraph StateGraph
│   ├── workflow.py        run_resume_workflow() — the single entry point
│   ├── router.py          conditional edge: validation -> rendering | retry
│   ├── executor.py        retry logic (re-runs only failed sections)
│   └── checkpoints.py      in-memory session checkpoint store
│
├── nodes/                 one file per graph node (upload, parser, planner,
│                           assembly, validation, rendering, evaluation)
│
├── agents/                 one folder per agent (planner + 8 generation agents)
│   └── base_agent.py       shared contract: load prompt -> call LLM -> parse -> apply
│
├── parsers/                pdf/, docx/, jd/, ocr/ — raw text extraction
├── prompts/                 one .txt file per agent — never hardcoded in .py
├── llm/                     llm_factory.py + provider clients (gemini/openai/anthropic)
├── schemas/                  every shape that crosses a boundary is a Pydantic model
├── services/                 orchestration glue used by the API routes
├── renderers/                 template_engine.py, html/pdf/docx renderers
├── templates/                 ats/, modern/, minimal/, academic/ — Jinja2 + CSS
├── validators/                 6 single-purpose validators (schema, ats, grammar,
│                                hallucination, consistency, duplicates)
├── evaluation/                 ats_score, keyword_score, resume_match, skill_gap,
│                                learning_resources, recommendation
├── utils/                       logger, constants, helpers, file/json utils, timing
├── database/                    optional persistence (no-ops if DATABASE_URL unset)
└── tests/                       mirrors the app/ structure 1:1
```

Every folder has one job. No file in the codebase exceeds ~150 lines —
see `AUDIT_REPORT.md` for the full reusability/monolith audit.

---

## 3. Shared state

Everything that flows through the graph is one Pydantic model,
`ResumeCopilotState` (`app/schemas/state_schema.py`):

```
files            FileMetadata        resume_path, jd_path
metadata         GraphMetadata       session_id, retry_count, errors  [merge reducer]
resume           ParsedResume         structured source resume
jd               ParsedJobDescription structured source job description
planning         PlanningOutput       the Planner's strategy (not resume content)
generated_sections  GeneratedSections  one field per agent's output    [merge reducer]
final_resume     GeneratedResume       assembled output
validation       ValidationReport      pass/fail per check
evaluation       EvaluationReport      scores + skill gap + resources
rendered_paths   dict[str, str]        exported file paths
```

`metadata` and `generated_sections` carry explicit merge reducers
(`merge_metadata`, `merge_generated_sections`) because they're the two
fields written concurrently during the parallel agent fan-out — without
a reducer, LangGraph raises `InvalidUpdateError` the moment two
branches write to the same channel in one step. Every other field is
written by exactly one node per step, so no reducer is needed there.

---

## 4. The LangGraph workflow — verified topology

This is the actual output of introspecting the compiled graph, not a
diagram drawn from the spec:

```
__start__
   │
   ▼
 upload  ──────────────────►  parser  ──────────────────►  planner
                                                               │
                    ┌──────────────────────────────────────────────────────────────┐
                    │                    parallel fan-out (8 agents)                │
                    ▼          ▼          ▼          ▼          ▼          ▼         ▼         ▼
                summary_   skills_    experience_ projects_  education_ certifications_ achievements_ links_
                 node       node        node        node       node          node           node        node
                    │          │          │          │          │             │              │            │
                    └──────────┴──────────┴──────────┴──────────┴─────────────┴──────────────┴────────────┘
                                                     ▼
                                                 assembly
                                                     │
                                                     ▼
                                                validation
                                                     │
                                    ┌────────────────┴────────────────┐
                                (overall_passed)              (validation failed)
                                    ▼                                  ▼
                                rendering                          retry
                                    │                                  │
                                    ▼                                  └──────► validation (loop)
                                evaluation
                                    │
                                    ▼
                                 __end__
```

Each of the 8 agent nodes has an edge **from** `planner` and an edge
**into** `assembly` — genuine fan-out/fan-in, all 8 execute concurrently
via `asyncio`, not sequentially. `retry` loops back into `validation`
rather than back into `assembly` directly, so a re-run always gets
re-checked before proceeding; `app/graph/router.py` caps this at
`MAX_VALIDATION_RETRIES` (default 2) so it can't loop forever.

To reproduce this exact output yourself:

```python
from app.graph.builder import build_graph
g = build_graph().get_graph()
print(list(g.nodes.keys()))
for e in g.edges:
    print(e.source, "->", e.target, "[conditional]" if e.conditional else "")
```

---

## 5. Request lifecycle (API → graph → response)

1. `POST /api/v1/upload/resume` and `/upload/jd` save files to disk and
   return a `file_id` each (`services/storage_service.py`).
2. `POST /api/v1/resume/generate` resolves those IDs back to paths
   (`services/parser_service.py`), builds the initial
   `ResumeCopilotState`, and calls `run_resume_workflow()`
   (`graph/workflow.py`), which invokes the compiled graph above and
   blocks until it reaches `__end__`.
3. The final state is cached in memory by `session_id`
   (`services/cache_service.py`) so `/evaluation` and
   `/templates/render` can be called again afterward without
   re-running the whole pipeline.
4. `/templates/download/{session_id}/{format}` streams the rendered
   file back directly.

---

## 6. Frontend ↔ backend contract

The frontend never guesses at response shapes — `frontend/js/api.js`
has one function per backend route, and the shapes it expects
(`GeneratedResume`, `EvaluationReport`, `ValidationReport`) match the
Pydantic schemas above exactly. If a backend schema changes,
`api.js` and `main.js`'s render functions are the only frontend files
that need to change.
