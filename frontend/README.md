# AI Resume Copilot — Frontend

A static, dependency-free frontend for the AI Resume Copilot backend.
No build step, no framework, no `node_modules` — open `index.html` or
serve the folder with any static file server.

## Files

```
frontend/
├── index.html        structure & copy
├── css/style.css      design system, layout, animation
├── js/config.js       the one place to set your API base URL
├── js/api.js          fetch wrapper, one function per backend route
├── js/main.js         page interactions & result rendering
└── assets/favicon.svg
```

## Running it

1. Start the backend (see `backend/README.md`):
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
2. Point the frontend at it — edit `js/config.js` if your backend isn't
   on `http://localhost:8000`.
3. Serve the frontend folder. Opening `index.html` directly works for
   viewing the design, but file uploads need a real HTTP origin for
   CORS, so use a static server:
   ```bash
   cd frontend
   python3 -m http.server 5500
   ```
   Then visit `http://localhost:5500`.

## CORS

The backend's `ALLOWED_ORIGINS` defaults to `["*"]` in
`backend/.env.example`, which accepts requests from any origin
including a local static server. Lock this down to your real frontend
origin before deploying either side publicly.

## What "Try it" actually does

1. Uploads your resume and job description to `/upload/resume` and
   `/upload/jd`.
2. Calls `/resume/generate`, which runs the full LangGraph pipeline
   server-side (parsing → planning → 8 parallel agents → validation →
   rendering → evaluation) and returns the tailored resume, validation
   report, and evaluation report in one response.
3. Renders the score, matched/missing skills, and a live resume
   preview from that response — no page reload, nothing hardcoded.
4. Export buttons hit `/templates/download/{session_id}/{format}`
   directly, which streams the real PDF/DOCX/HTML back from the
   backend's renderer.

The agent progress grid mid-generation is a **visual approximation**:
the real backend call is a single blocking request (see the FUTURE
note in `index.html` about moving to SSE/WebSocket for true per-agent
progress), so the UI animates through the 8 agent names on a timer
and then snaps to "done" the moment the real response lands.

## Design notes

Uses the system font stack (`-apple-system, BlinkMacSystemFont…`)
rather than a webfont import, so Apple devices render actual SF Pro —
no CDN dependency, works fully offline. Color tokens, spacing, and
radii are all defined once at the top of `css/style.css`.
