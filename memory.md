# AI Tutor — Project Memory

## Phase 0: Seed Data (Completed 2026-09-02)
Created 4 JSON seed files for Ch2 Quadratic Equations: 16 concepts, 51 questions, 14 prerequisite edges, 12 misconceptions. All cross-references verified. 5 LLM prompt templates (system, teach, diagnose, hint, scaffold) created in `data/prompts/`. Initial assessment (15 questions) created.

## Phase 1: Backend Foundation (Completed 2026-09-03)
FastAPI project in `backend/` with pydantic-settings config, structlog logging, and asyncpg connection pool. 5 Pydantic model files (enums, curriculum, student, session, mastery) matching architecture doc. 3 repository classes (curriculum, student, mastery) with idempotent upsert operations. SQL migration `001_initial_schema.sql` creates 9 tables with constraints and indexes. Import script `scripts/import_seed_data.py` is idempotent. Health endpoint at `/health`. 25 tests passing — models validated against all seed JSON. Server handles missing DB gracefully.
