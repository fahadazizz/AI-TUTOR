# AI Tutor — Codebase Rules

## Project Identity
- **Product**: AI-powered Urdu tutor for Class 10 (Punjab Board, Pakistan)
- **Stack**: FastAPI (Python) backend + Next.js (TypeScript) frontend + Supabase (PostgreSQL)
- **LLM Providers**: Groq API (primary, cloud) + Ollama (local dev/testing)
- **Target**: Production-ready, mobile-first PWA

## Architecture Rules
1. The LLM is the language engine, NOT the brain. All routing, mastery tracking, question selection, and answer checking are deterministic Python.
2. The Tutor Controller (`tutor_controller.py`) must contain ZERO LLM calls. It is a pure state machine.
3. Every LLM call goes through `llm_client.py`. No direct API calls from other modules.
4. Every LLM response passes through `guardrails.py` before reaching the student.
5. Mathematical answer checking uses SymPy (deterministic), never the LLM.
6. Curriculum data lives in structured JSON/DB, not vector embeddings. No RAG for V1.

## Python Backend Rules
- Python 3.11+. Use type hints on ALL function signatures.
- All data models use Pydantic BaseModel with strict validation.
- All database queries go through repository classes (not raw SQL in route handlers).
- Environment variables via `pydantic-settings`. Never hardcode API keys or URLs.
- Async everywhere: all route handlers, DB calls, and LLM calls must be `async def`.
- Error handling: return structured JSON errors, never expose stack traces to client.
- Logging: use `structlog` with JSON output. Log every LLM call with token count and latency.
- Tests: `pytest` + `pytest-asyncio`. Minimum one test per public function.

## TypeScript Frontend Rules
- Next.js 15 App Router. No Pages Router.
- All components are functional with TypeScript (`.tsx`). No `any` types.
- API calls go through a single `api.ts` client module.
- Urdu text must render RTL. Use `dir="rtl"` on Urdu containers.
- Math formulas rendered via KaTeX. LaTeX strings come from the backend.
- Mobile-first: design for 360px width, then scale up.
- PWA: service worker caches UI shell. Offline shows graceful fallback.

## LLM Integration Rules
- Primary: Groq API (Llama/Mixtral models via Groq cloud).
- Dev/Testing: Ollama (local models, no API cost).
- `llm_client.py` must support both providers via a unified interface.
- All LLM calls use structured output (JSON mode) where possible.
- System prompts are stored in `data/prompts/` as text files, not hardcoded.
- Never send the expected answer to the LLM when scaffolding mode is active.
- Retry failed LLM calls 3 times with exponential backoff before returning error.
- Log every LLM call: model, tokens_in, tokens_out, latency_ms, cost_estimate.

## Data Rules
- Curriculum data (concepts, questions, misconceptions) lives in `data/curriculum/`.
- All JSON data files must pass schema validation before import.
- Every `concept_id`, `question_id`, `misconception_id` must be globally unique.
- Cross-references between JSON files must resolve (no dangling IDs).
- Database migrations are forward-only. Never modify existing migration files.
- Seed data import scripts must be idempotent (safe to run multiple times).

## Testing Rules
- Unit tests for all deterministic logic (mastery transitions, answer checking, question selection).
- Integration tests for API endpoints (use `httpx.AsyncClient`).
- LLM-dependent tests are tagged `@pytest.mark.llm` and skipped in CI by default.
- All SymPy answer checks must be tested against every question in the seed data.
- Test names describe the scenario: `test_mastery_transitions_to_struggling_after_3_wrong`.

## Security Rules
- All LLM API calls route through the backend. Frontend never touches LLM APIs.
- Student data is isolated: queries always filter by `student_id`.
- Input sanitization: SymPy's `sympify` runs in a restricted namespace (no `eval`).
- Rate limit: 60 requests/minute per student on chat endpoint.

## Documentation Rules
- Do not overwrite the Implmentation Plan Artifact as it is the standalone Implimentation plan Roadmap for proper buliding and testing... Use another Artifact as Build Plan for phase wise planning 
- Preserve all existing comments unless the code they describe is deleted.
- Every module has a docstring explaining its role in the architecture.
- Complex algorithms (prerequisite graph traversal, mastery updates) get inline comments.
- API endpoints have docstrings that become OpenAPI documentation.

## Git Rules
- Commit messages: `phase-X: short description` (e.g., `phase-2: add sympy answer checker`).
- Never commit `.env`, API keys, or student data to version control.
- `.gitignore` must include: `.env`, `__pycache__`, `node_modules`, `.next`, `*.pyc`.
