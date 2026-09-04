# AI Tutor — Complete Implementation Plan & Roadmap

> **Status**: Living document. Updated to reflect actual completed V0 milestones and the true grand vision from `PROJECT_CONTEXT.md`.

---

## Guiding Principles
1. **Prove the tutoring loop first.** (Achieved in V0).
2. **One subject, one chapter.** Mathematics Chapter 2 (Quadratic Equations) is the pilot.
3. **Deterministic core, generative surface.** All routing, mastery tracking, and answer checking are deterministic Python (SymPy). Only explanation generation uses the LLM.
4. **Structured Knowledge over Unstructured RAG.** The curriculum is defined as structured JSON files (Concepts, Prerequisites, Misconceptions). We do not blindly RAG over entire textbook PDFs; we use precise structured lookup.

---

## Phase Overview & Progress Summary

| Phase | Name | Status | Core Deliverable |
|:------|:-----|:-------|:-----------------|
| **0** | Seed Data Completion | ✅ **Completed** | Seed JSON for Math Chapter 2 (Concepts, Prereqs, 22 Questions) |
| **1** | Backend Foundation | ✅ **Completed** | FastAPI, PostgreSQL Schema, Local Migration |
| **2** | Core Engine | ✅ **Completed** | Student Model (State Machine), SymPy Math Checker, Curriculum Model |
| **3** | Tutor Controller & LLM | 🚧 **In Progress (V0 done)** | Intent Routing, LLM Generation, (Missing: Strict Guardrails & Prereq Blocking) |
| **4** | API Layer | 🚧 **In Progress (V0 done)** | Chat, Assessment, Progress APIs (Missing: SSE Streaming) |
| **5** | Frontend Chat UI (PWA) | ✅ **Completed** | Digital Slate theme, RTL Urdu, KaTeX, Progress Map |
| **6** | Integration Validation | 🚧 **In Progress** | Basic flow working. Needs Scaffolding & Edge Case validation. |
| **7** | Production Hardening | ⏳ **Planned** | Streaming, Guardrails, Deployment |
| **8** | Data-Driven Intelligence | ⏳ **Planned** | Spaced Repetition (SM-2), Bayesian Knowledge Tracing (BKT) |
| **9** | Multi-Subject Pedagogy | ⏳ **Planned** | Physics Engine, Chemistry Pedagogy |
| **10** | Multi-Modal & Exams | ⏳ **Planned** | Image Upload (OCR), Voice (STT/TTS), Board Exam Mode |

---

## Detailed Phase Breakdown

### Phases 0 - 2: Foundation (Completed)
*   **Database & API:** Fully functional FastAPI backend connected to PostgreSQL. `student_mastery` is robustly tracked.
*   **UI Foundation:** Next.js PWA built with the bespoke Digital Slate theme. Assessment and Progress visualization fully operational.
*   **Math Checker:** SymPy integrated to deterministically evaluate algebraic equivalence.

### Phase 3 & 4 Completion: Controller & API Hardening (Current Immediate Focus)
*   **3.1 Prerequisite Traversal:** Upgrade `tutor_controller.py` to actively query the prerequisite DAG. If a student asks for the Quadratic Formula but lacks Discriminant mastery, the system must pivot.
*   **3.2 Strict Scaffolding:** Enforce the rule: *Never give the answer.* Ensure `TEACH_CONCEPT` with scaffolding mode asks step-by-step questions instead of monolithic explanations.
*   **3.3 Misconception Routing:** Wire `math_checker.py` error types (like `sign_error`) directly to the `misconceptions.json` remediation strategies.
*   **3.4 Strict Guardrails:** Complete `guardrails.py` to actively block answer leaks and language drift (enforcing Urdu ratios).
*   **4.1 Server-Sent Events (SSE):** Convert `/api/chat` to a streaming endpoint so the UI updates token-by-token, eliminating the 20-second wait time.

### Phase 7: Deployment & Real-World Launch
*   **7.1 Database Migration:** Move from local PostgreSQL to a cloud Supabase instance.
*   **7.2 Hosting:** Deploy the FastAPI backend to Render/Railway and the Next.js frontend to Vercel.
*   **7.3 LLM Cloud Provider:** Transition from local Ollama testing back to a cloud provider (e.g., Groq Llama3 or GPT-4o-mini) for always-on availability.

### Phase 8: Data-Driven Intelligence
*   **8.1 Spaced Repetition (SM-2):** Implement a background cron or session-start logic to decay `MASTERED` states to `NEEDS_REVIEW` based on time intervals (Day 1, 3, 7, 14).
*   **8.2 Bayesian Knowledge Tracing (BKT):** Once 500+ interactions are logged, transition the Student Model from a simple State Machine to probabilistic float scores (`0.0` to `1.0`).
*   **8.3 Curriculum Expansion:** Generate complete structured JSON seed data for the remaining Class 10 Math chapters.

### Phase 9: Multi-Subject Pedagogy
*   **9.1 Subject-Specific Controllers:** Implement distinct pedagogy loops.
    *   *Physics:* `Given -> Find -> Formula -> Substitute -> Unit` (Unit and significant figure checking).
    *   *Chemistry:* Reaction mechanisms, definitions, balanced equations.
    *   *Biology:* Terminology and diagram conceptual descriptions.
*   **9.2 Physics Checker:** Extend the verification engine to validate standard metric units alongside numerical answers.

### Phase 10: Multi-Modal Interaction & Board Prep
*   **10.1 Image Upload (Vision API):** Allow students to upload a photo of a textbook question. Use OCR to extract the math/text, map it to a `concept_id`, and initiate tutoring.
*   **10.2 Voice Interface:** Integrate lightweight STT (Speech-to-Text) so students can speak their questions in Urdu, and TTS for spoken responses.
*   **10.3 Board Exam Layer:** Implement `EXAM MODE` which generates full mock papers, times the session, and performs a post-exam error analysis loop.

---
