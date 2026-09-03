"""
AI Tutor — Curriculum Repository.

Database access layer for concepts, questions, misconceptions,
and prerequisite relationships. This is where seed data gets
imported into the database and where the Curriculum Model reads from.
"""

import json

from app.repositories.base import BaseRepository


class CurriculumRepository(BaseRepository):
    """Repository for curriculum data (concepts, questions, misconceptions)."""

    # ── Concepts ────────────────────────────────────

    async def upsert_concept(
        self,
        concept_id: str,
        subject_id: str,
        chapter: int,
        chapter_name: str,
        name_en: str,
        name_ur: str,
        difficulty: int,
        textbook_page: str | None,
        pedagogy_type: str,
        learning_objectives: list,
        formulas: list,
        explanation_ur: str,
        key_terms: list,
        worked_examples: list,
    ) -> None:
        """Insert or update a concept (idempotent)."""
        await self._execute(
            """
            INSERT INTO concepts (
                concept_id, subject_id, chapter, chapter_name,
                name_en, name_ur, difficulty, textbook_page,
                pedagogy_type, learning_objectives, formulas,
                explanation_ur, key_terms, worked_examples
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
            ON CONFLICT (concept_id) DO UPDATE SET
                subject_id = EXCLUDED.subject_id,
                chapter = EXCLUDED.chapter,
                chapter_name = EXCLUDED.chapter_name,
                name_en = EXCLUDED.name_en,
                name_ur = EXCLUDED.name_ur,
                difficulty = EXCLUDED.difficulty,
                textbook_page = EXCLUDED.textbook_page,
                pedagogy_type = EXCLUDED.pedagogy_type,
                learning_objectives = EXCLUDED.learning_objectives,
                formulas = EXCLUDED.formulas,
                explanation_ur = EXCLUDED.explanation_ur,
                key_terms = EXCLUDED.key_terms,
                worked_examples = EXCLUDED.worked_examples
            """,
            concept_id, subject_id, chapter, chapter_name,
            name_en, name_ur, difficulty, textbook_page,
            pedagogy_type,
            json.dumps(learning_objectives, ensure_ascii=False),
            json.dumps(formulas, ensure_ascii=False),
            explanation_ur,
            json.dumps(key_terms, ensure_ascii=False),
            json.dumps(worked_examples, ensure_ascii=False),
        )

    async def get_concept(self, concept_id: str) -> dict | None:
        """Fetch a single concept by ID."""
        row = await self._fetch_one(
            "SELECT * FROM concepts WHERE concept_id = $1", concept_id
        )
        return dict(row) if row else None

    async def get_concepts_by_subject(self, subject_id: str) -> list[dict]:
        """Fetch all concepts for a subject, ordered by chapter and difficulty."""
        rows = await self._fetch_all(
            """
            SELECT * FROM concepts
            WHERE subject_id = $1
            ORDER BY chapter, difficulty
            """,
            subject_id,
        )
        return [dict(r) for r in rows]

    async def get_concept_count(self) -> int:
        """Count total concepts in the database."""
        row = await self._fetch_one("SELECT COUNT(*) as cnt FROM concepts")
        return row["cnt"] if row else 0

    # ── Prerequisites ───────────────────────────────

    async def upsert_prerequisite(self, concept_id: str, prerequisite_id: str) -> None:
        """Insert a prerequisite edge (idempotent)."""
        await self._execute(
            """
            INSERT INTO concept_prerequisites (concept_id, prerequisite_id)
            VALUES ($1, $2)
            ON CONFLICT (concept_id, prerequisite_id) DO NOTHING
            """,
            concept_id, prerequisite_id,
        )

    async def get_prerequisites(self, concept_id: str) -> list[str]:
        """Get all prerequisite concept IDs for a concept."""
        rows = await self._fetch_all(
            "SELECT prerequisite_id FROM concept_prerequisites WHERE concept_id = $1",
            concept_id,
        )
        return [r["prerequisite_id"] for r in rows]

    async def get_prerequisite_count(self) -> int:
        """Count total prerequisite edges."""
        row = await self._fetch_one("SELECT COUNT(*) as cnt FROM concept_prerequisites")
        return row["cnt"] if row else 0

    # ── Questions ───────────────────────────────────

    async def upsert_question(
        self,
        question_id: str,
        concept_id: str,
        difficulty: int,
        question_type: str,
        question_text_ur: str,
        question_text_en: str,
        expected_answer: str,
        answer_tolerance: float | None,
        expected_answer_unit: str | None,
        solution_steps: list,
        hints: list,
        tags: list,
    ) -> None:
        """Insert or update a question (idempotent)."""
        await self._execute(
            """
            INSERT INTO questions (
                question_id, concept_id, difficulty, question_type,
                question_text_ur, question_text_en, expected_answer,
                answer_tolerance, expected_answer_unit,
                solution_steps, hints, tags
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
            ON CONFLICT (question_id) DO UPDATE SET
                concept_id = EXCLUDED.concept_id,
                difficulty = EXCLUDED.difficulty,
                question_type = EXCLUDED.question_type,
                question_text_ur = EXCLUDED.question_text_ur,
                question_text_en = EXCLUDED.question_text_en,
                expected_answer = EXCLUDED.expected_answer,
                answer_tolerance = EXCLUDED.answer_tolerance,
                expected_answer_unit = EXCLUDED.expected_answer_unit,
                solution_steps = EXCLUDED.solution_steps,
                hints = EXCLUDED.hints,
                tags = EXCLUDED.tags
            """,
            question_id, concept_id, difficulty, question_type,
            question_text_ur, question_text_en, expected_answer,
            answer_tolerance, expected_answer_unit,
            json.dumps(solution_steps, ensure_ascii=False),
            json.dumps(hints, ensure_ascii=False),
            json.dumps(tags, ensure_ascii=False),
        )

    async def get_questions_by_concept(self, concept_id: str) -> list[dict]:
        """Fetch all questions for a concept, ordered by difficulty."""
        rows = await self._fetch_all(
            "SELECT * FROM questions WHERE concept_id = $1 ORDER BY difficulty",
            concept_id,
        )
        return [dict(r) for r in rows]

    async def get_question_count(self) -> int:
        """Count total questions in the database."""
        row = await self._fetch_one("SELECT COUNT(*) as cnt FROM questions")
        return row["cnt"] if row else 0

    # ── Misconceptions ──────────────────────────────

    async def upsert_misconception(
        self,
        misconception_id: str,
        concept_id: str,
        subject_key: str,
        description_en: str,
        description_ur: str,
        severity: str,
        error_patterns: list,
        prerequisite_gap: str | None,
        remediation_strategy: str,
        remediation_explanation_ur: str,
        diagnostic_question_ids: list,
        practice_question_ids: list,
    ) -> None:
        """Insert or update a misconception (idempotent)."""
        await self._execute(
            """
            INSERT INTO misconceptions (
                misconception_id, concept_id, subject_key,
                description_en, description_ur, severity,
                error_patterns, prerequisite_gap,
                remediation_strategy, remediation_explanation_ur,
                diagnostic_question_ids, practice_question_ids
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
            ON CONFLICT (misconception_id) DO UPDATE SET
                concept_id = EXCLUDED.concept_id,
                subject_key = EXCLUDED.subject_key,
                description_en = EXCLUDED.description_en,
                description_ur = EXCLUDED.description_ur,
                severity = EXCLUDED.severity,
                error_patterns = EXCLUDED.error_patterns,
                prerequisite_gap = EXCLUDED.prerequisite_gap,
                remediation_strategy = EXCLUDED.remediation_strategy,
                remediation_explanation_ur = EXCLUDED.remediation_explanation_ur,
                diagnostic_question_ids = EXCLUDED.diagnostic_question_ids,
                practice_question_ids = EXCLUDED.practice_question_ids
            """,
            misconception_id, concept_id, subject_key,
            description_en, description_ur, severity,
            json.dumps(error_patterns, ensure_ascii=False),
            prerequisite_gap,
            remediation_strategy, remediation_explanation_ur,
            json.dumps(diagnostic_question_ids, ensure_ascii=False),
            json.dumps(practice_question_ids, ensure_ascii=False),
        )

    async def get_misconception_count(self) -> int:
        """Count total misconceptions in the database."""
        row = await self._fetch_one("SELECT COUNT(*) as cnt FROM misconceptions")
        return row["cnt"] if row else 0

    # ── Subjects ────────────────────────────────────

    async def upsert_subject(
        self, subject_id: str, name_en: str, name_ur: str
    ) -> None:
        """Insert or update a subject (idempotent)."""
        await self._execute(
            """
            INSERT INTO subjects (id, name_en, name_ur)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO UPDATE SET
                name_en = EXCLUDED.name_en,
                name_ur = EXCLUDED.name_ur
            """,
            subject_id, name_en, name_ur,
        )
