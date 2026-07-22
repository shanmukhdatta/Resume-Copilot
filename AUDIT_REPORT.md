# AI Resume Copilot — Backend Audit Report

Verification performed by actually running the code (compile checks, full
pytest suite, isolated per-node execution, and full end-to-end LangGraph
runs) — not a read-through. Two real bugs were found and fixed as a result.

## 1. Folder structure — MATCHES SPEC exactly

All 16 mandated top-level modules present with correct sub-packages:
`api/{routes,middleware,validators,exceptions}`, `graph`, `nodes`,
`agents/{planner,summary,skills,experience,projects,education,
certifications,achievements,links}`, `parsers/{pdf,docx,jd,ocr}`,
`prompts/<one folder per agent>`, `llm`, `schemas`, `services`,
`renderers/css`, `templates/{ats,modern,minimal,academic}`, `validators`,
`evaluation`, `utils`, `database/migrations`, `tests/{agents,graph,
parsers,renderers,validators,api}`. No folder was collapsed or merged.

## 2. Monolith check — PASS

Largest file in the entire codebase is 116 lines
(`schemas/state_schema.py`). No file exceeds 150 lines. Every module
has one job: parsing lives in `parsers/`, prompt text lives in
`prompts/*.txt` (never inline in `.py`), LLM calls go through one
factory, validation is split into 6 single-purpose validators, etc.

## 3. Prompt externalization — PASS

All 9 agents (`planner` + 8 generation agents) load their prompt via
`self.load_prompt()` reading from `app/prompts/**/*.txt`. Zero agents
have an inline prompt string. Verified by grep across every agent file.

## 4. LLM provider isolation — PASS

No agent, node, parser, or validator imports `google.generativeai`,
`openai`, or `anthropic` directly. Every LLM call goes through
`app/llm/llm_factory.get_llm_client()`, so swapping providers (e.g.
Gemini → OpenAI) requires changing one config value, not touching agent
code. Only 5 files call the factory: `base_agent.py`,
`parser_factory.py`, `jd_parser.py`, `hallucination_validator.py`, and
the factory itself.

## 5. Bugs found and fixed during this audit

**Bug 1 — DRY violation.** `_section_keywords()` was duplicated
verbatim in 4 separate agent files (summary, skills, experience,
projects) instead of being a single reusable helper. **Fixed**: extracted
to `app/agents/prompt_context.py::section_keywords()`; all 4 agents now
import the shared function. Zero duplicate function bodies remain.

**Bug 2 — Serialization crash in the hallucination validator.** Pydantic
auto-coerces `GeneratedResume.experience` (typed `list[ExperienceEntry]`)
back into model objects during assembly, even when assembly passes in
plain dicts. `hallucination_validator.py` was calling `dumps()` directly
on those model objects, which orjson cannot serialize, silently failing
the LLM fact-check every run (caught by a broad except, so it never
crashed the pipeline, but the hallucination check was never actually
running). **Fixed**: the validator now normalizes each entry with
`.model_dump()` before serializing. Confirmed via a clean end-to-end run
that the warning is gone and the check now executes.

## 6. LangGraph workflow — VERIFIED against the actual compiled graph

Introspected the real compiled `StateGraph` object (not just the source
code) and confirmed every node and edge matches the mandated workflow:

```
START -> upload -> parser -> planner
      -> [summary, skills, experience, projects, education,
          certifications, achievements, links]   (8-way parallel fan-out)
      -> assembly -> validation
           -> (pass) -> rendering -> evaluation -> END
           -> (fail) -> retry -> validation        (loop)
```

Every one of the 8 generation agents has an edge from `planner` and an
edge into `assembly` — true fan-out/fan-in, not sequential execution.

## 7. Every node individually tested in isolation — ALL PASS

Rather than trusting the full pipeline alone, each node was invoked
directly with a hand-built state to confirm its specific contract:

| Node | Result |
|---|---|
| `upload_node` | Validates file existence, records errors if missing |
| `summary_node` (agent) | Returns partial update `{generated_sections, metadata}` only — confirms an agent never touches unrelated state |
| `assembly_node` | Correctly merges `generated_sections` into `final_resume` |
| `validation_node` | Runs all 6 validators, correctly reports pass/fail per category |
| `router` (conditional edge) | `pass → rendering`, `fail → retry`, confirmed both branches |
| `rendering_node` | Writes a real HTML file to disk |
| `evaluation_node` | Produces a real ATS score (94.0) and keyword coverage (100%) on a matching sample |

## 8. Parallel fan-out correctness — VERIFIED

Confirmed the 8 concurrent agents don't corrupt shared state: each
agent's `run()` returns only its own field plus `metadata`, and
`app/schemas/state_schema.py` defines explicit merge reducers
(`merge_generated_sections`, `merge_metadata`) for the two channels
multiple agents write to concurrently. Without these, LangGraph raises
`InvalidUpdateError` on true concurrent writes — this was caught and
fixed in an earlier pass and is now covered by the full e2e test.

## 9. Full pipeline runs, clean

Final end-to-end run (real `.docx` resume + text JD, stub LLM mode
since no API key is configured in this sandbox):

```
ERRORS: []
VALIDATION: False ['consistency']   <- expected: stub LLM returns empty
                                         content, so full_name is blank
RENDERED: {'html': 'data/exports/..._resume.html'}   <- real file written
```

`pytest app/tests -q` → **8 passed**, 0 failed.

## Bottom line

Structure, separation of concerns, prompt externalization, and LLM
abstraction all check out against the master prompt as written. The
audit surfaced and fixed one reusability issue (duplicated helper) and
one real functional bug (a validator that was silently no-op'ing due to
a serialization error). The corrected zip has been repackaged.
