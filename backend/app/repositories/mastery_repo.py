"""
AI Tutor — Mastery Repository.

Database access layer for student mastery records.
"""

import json
import uuid
from datetime import datetime

from app.repositories.base import BaseRepository


class MasteryRepository(BaseRepository):
    """Repository for student mastery state data."""

    async def get_mastery(
        self, student_id: uuid.UUID, concept_id: str
    ) -> dict | None:
        """Get a student's mastery record for a specific concept."""
        row = await self._fetch_one(
            """
            SELECT * FROM student_mastery
            WHERE student_id = $1 AND concept_id = $2
            """,
            student_id, concept_id,
        )
        return dict(row) if row else None

    async def get_all_mastery(self, student_id: uuid.UUID) -> list[dict]:
        """Get all mastery records for a student."""
        rows = await self._fetch_all(
            "SELECT * FROM student_mastery WHERE student_id = $1",
            student_id,
        )
        return [dict(r) for r in rows]

    async def upsert_mastery(
        self,
        student_id: uuid.UUID,
        concept_id: str,
        mastery_state: str,
        consecutive_correct: int,
        consecutive_wrong: int,
        total_attempts: int,
        total_correct: int,
        last_attempt_at: datetime | None,
        mastered_at: datetime | None,
        misconception_ids: list[str],
    ) -> None:
        """Insert or update a mastery record (idempotent)."""
        await self._execute(
            """
            INSERT INTO student_mastery (
                student_id, concept_id, mastery_state,
                consecutive_correct, consecutive_wrong,
                total_attempts, total_correct,
                last_attempt_at, mastered_at, misconception_ids, updated_at
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,now())
            ON CONFLICT (student_id, concept_id) DO UPDATE SET
                mastery_state = EXCLUDED.mastery_state,
                consecutive_correct = EXCLUDED.consecutive_correct,
                consecutive_wrong = EXCLUDED.consecutive_wrong,
                total_attempts = EXCLUDED.total_attempts,
                total_correct = EXCLUDED.total_correct,
                last_attempt_at = EXCLUDED.last_attempt_at,
                mastered_at = EXCLUDED.mastered_at,
                misconception_ids = EXCLUDED.misconception_ids,
                updated_at = now()
            """,
            student_id, concept_id, mastery_state,
            consecutive_correct, consecutive_wrong,
            total_attempts, total_correct,
            last_attempt_at, mastered_at,
            json.dumps(misconception_ids),
        )
