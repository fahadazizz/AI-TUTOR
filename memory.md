# AI Tutor — Project Memory

## Phase 0: Seed Data (Completed 2026-09-02)
Created 4 JSON seed files for Ch2 Quadratic Equations: 16 concepts, 51 questions, 14 prerequisite edges, 12 misconceptions. All cross-references verified. 5 LLM prompt templates (system, teach, diagnose, hint, scaffold) created in `data/prompts/`. Initial assessment (15 questions) created.

## Phase 1: Backend Foundation (Completed 2026-09-03)
FastAPI project in `backend/` with pydantic-settings config, structlog logging, and asyncpg connection pool. 5 Pydantic model files (enums, curriculum, student, session, mastery) matching architecture doc. 3 repository classes (curriculum, student, mastery) with idempotent upsert operations. SQL migration `001_initial_schema.sql` creates 9 tables with constraints and indexes. Import script `scripts/import_seed_data.py` is idempotent. Health endpoint at `/health`. 25 tests passing — models validated against all seed JSON. Server handles missing DB gracefully. Data imported into a local Docker Postgres DB running on port 55325.

## Phase 2: Core Engine (Completed 2026-09-04)
Implemented the foundational deterministic engines in `app/core/`:
- **Math Checker**: Uses `sympy` to verify student answers, normalize math strings (e.g., `x2` to `x**2`), and detect specific mistakes (e.g., sign errors, providing only one root).
- **Curriculum Model**: DFS traversal to find deepest missing prerequisites, plus cycle detection.
- **Student Model**: Implements the exact 8-state mastery transition logic based on student attempt history.
- **Question Selector**: Dynamically picks the appropriate difficulty question based on the student's mastery state and past seen questions.
All 48 backend tests (including 23 new core logic tests) are passing flawlessly.

## Phase 3: Tutor Controller & Teaching Engine (Completed 2026-09-04)
Integrated LLMs with the deterministic core via `app/tutor/`:
- **LLM Client**: `httpx` based client with exponential backoff and JSON mode for Ollama/Groq.
- **Language Layer**: Parses unstructured user text into a strict `StudentIntent` schema using LLM structured output.
- **Tutor Controller**: Pure deterministic state machine that maps intent + student state to a `TutorAction`.
- **Teaching Engine**: Generates Urdu responses based on the chosen action.
- **Guardrails**: Prevents answer leakage, blocks overly long texts, and detects language drift (e.g., Hindi script).
- **Rule 7 Validation**: Successfully ran a live end-to-end interactive CLI session (`scripts/interactive_tutor.py`) confirming the LLM loop functions properly in practice.
