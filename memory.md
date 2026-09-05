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

## Phase 4: API Layer & Session Management (Completed 2026-09-04)
Exposed the AI Tutor loop as a stateful FastAPI application connected to Supabase PostgreSQL:
- **Session Manager & Repo**: Connects to DB via `asyncpg` to persist tutoring sessions (`SessionCreate`, `AttemptCreate`) across requests.
- **Auth Router (`/api/auth`)**: Endpoints for student registration, login, and creating new tutoring sessions.
- **Progress Router (`/api/progress`)**: Endpoints to fetch a student's mastery state.
- **Chat Router (`/api/chat`)**: The core interaction loop. Receives messages, orchestrates intent detection + tutor decision + LLM generation + guardrails + DB updates, and returns a JSON response.
- **Rule 7 Validation**: Created `scripts/test_api_live.sh` which boots a background Uvicorn server, hits real endpoints with `curl`, and proved that the entire system successfully registers students, creates DB sessions, and answers math queries over HTTP.

## Phase 5: Frontend Foundations (Completed 2026-09-04)
Built a modern, bespoke Next.js 15 PWA designed to minimize cognitive load and avoid typical "AI Slop" aesthetics.
- **Next.js 15 App Router**: Scaffolded with TypeScript, vanilla CSS, and strictly no Tailwind to adhere to rules.
- **Digital Slate Theme**: Created a custom `globals.css` theme utilizing deep charcoals, sage greens, and muted slates. Built bespoke CSS modules (`Button.module.css`, `Chat.module.css`) implementing subtle glassmorphism instead of generic pill-shaped components.
- **RTL & Typography**: Integrated `Noto Nastaliq Urdu` exclusively for Urdu tutor responses (enforcing strict Right-to-Left layout) while maintaining `Outfit` for the English UI elements. 
- **KaTeX Integration**: Implemented a robust `MathRenderer` capable of parsing block (`$$`) and inline (`$`) LaTeX strings emitted by the backend.
- **API Client**: Implemented `src/lib/api.ts` providing typed wrappers for FastAPI backend endpoints.
- **Core Pages**: Developed a serene Landing Page (`/`) to begin sessions, and a full-featured Chat Interface (`/chat`) with quick-insert math buttons (², √, ±, ÷).

## Phase 6 & 7: System Hardening (Completed 2026-09-04)
Fully completed the backend and frontend system hardening to reach production-ready stability.
- **SSE Streaming**: Implemented Server-Sent Events in `llm_client.py`, `/api/chat/stream`, and Next.js frontend, enabling real-time typing responses.
- **Strict Logic**: Enforced strict prerequisite traversal (teaching missing basics first), enforced step-by-step scaffolding (preventing full problem-solving), and routed partial/sign errors to targeted misconception checks.
- **Guardrails**: Added word-boundary regex detection to strictly block the generative layer from leaking the exact expected answer, while preserving performance on single-character answers. All 63 backend tests pass successfully.

## Phase 8: Multi-Language & Prompt Overhaul (Completed 2026-09-04)
- **Prompt Engineering**: Removed compacted English prompts from the generative engine. Implemented a robust `PromptManager` loading language-specific constraints (English, Native Urdu Nastaliq, Roman Urdu) directly from `data/prompts/` text/JSON files, completely eliminating language drift.
- **Dynamic Controller Routing**: Hooked `TutorController` directly into `QuestionSelector` for `CONTINUE` intents, breaking the LLM out of "constant motivation" loops and forcing true scaffolding behavior.
- **UI Language Switcher**: Made language context strictly persist through the session dictionary and auto-trigger a context-aware backend initialization on first chat load.

## Phase 9: Language Routing Fixes (Completed 2026-09-04)
- Fixed a major bug in `TeachingEngine` where missing concept names caused a fallback to the English string `"basic concept"`, which confused the LLM and forced it to reply in English regardless of the selected language.
- Refactored `_build_prompt_for_action` to correctly extract `name_ur` (for Nastaliq) or `name_en` (for Roman Urdu/English) based on the active session's language preference.
- Updated `chat.py` and `teaching_engine.py` to forward the raw student message into the final LLM prompt context to allow nuance handling, while maintaining the safety of the Controller architecture.

## Phase A (V0.0 & V0.1): Schema Generalization & Foundation (Completed 2026-09-05)
- Generalized the curriculum `Concept` schema to include `board`, `grade`, `visual_need`, `language_pack`, and `textbook_sources` fields to support multi-board scalability.
- Successfully verified database reads/writes and confirmed `ollama` LLM connectivity via `verify_v0_0.py`.
- Phase A V0.2 Done: Implemented persistent core mastery loop via TutorController and ChatRouter to securely store state and attempts.
- Phase A V0.3 Done: Fully validated deterministic symbolic math verifier using SymPy. Tested against 30 unique real-world edge cases. Checked that no LLM call is made.
- Phase A V0.4 Done: Solved equation rendering. Migrated all JSON seed data to use standard LaTeX ($) for math fields. Updated English, Urdu, and Roman Urdu system prompts to strictly mandate LaTeX formatting and forbid bare unicode math or unescaped parens. Verified correct LLM parsing and KaTeX frontend rendering.
- Phase A V0.5 Done: Developed the Visual Engine. Defined `visual_need` tags in the curriculum for graphs/diagrams. Created 8 beautiful bespoke React SVG components (`ParabolaGraph`, `NumberLine`, `SystemGraph`, `CompletingSquare`, `QuadraticFormula`, `RootsNature`, `AreaModel`, `DependencyTree`) and integrated a shortcode parser in `ChatBubble.tsx` to deterministically insert these based on backend prompt instructions.
- Phase A V0.6 Done: Populated Misconception Library for Chapter 2. Updated MathChecker and TutorController to deterministically match wrong student answers against specific algebraic error triggers using SymPy. System successfully intercepts known errors and injects targeted pedagogical remediation instead of relying on generative LLM diagnosis.
- Phase A V0.7 Done: Built the persistent progress dashboard at /progress. Implemented a deterministic topological graph layout algorithm in TypeScript to visually render the concept dependencies as an SVG-powered Directed Acyclic Graph (DAG) directly reading from Curriculum and Student Models.
