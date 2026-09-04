"""
AI Tutor — Session Repository.

Handles database operations for Sessions and Attempts.
"""

import uuid
import json
from typing import Optional

from app.repositories.base import BaseRepository
from app.models.session import Session, SessionCreate, AttemptCreate
from app.logging import get_logger

logger = get_logger(__name__)


class SessionRepository(BaseRepository):
    """PostgreSQL repository for Session data."""

    async def create_session(self, session_data: SessionCreate) -> Session:
        """Create a new session."""
        session_id = uuid.uuid4()
        query = """
            INSERT INTO sessions (id, student_id, subject_key, started_at, is_active, session_state)
            VALUES ($1, $2, $3, NOW(), TRUE, '{}'::jsonb)
            RETURNING id, student_id, subject_key, started_at, ended_at, 
                      current_concept_id, current_question_id, session_state, 
                      hint_level, scaffold_step, is_active, summary, total_exchanges
        """
        row = await self._fetch_one(query, session_id, session_data.student_id, session_data.subject_key)
        
        state = row["session_state"]
        if isinstance(state, str):
            state = json.loads(state)
            
        return Session(
            id=row["id"],
            student_id=row["student_id"],
            subject_key=row["subject_key"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            current_concept_id=row["current_concept_id"],
            current_question_id=row["current_question_id"],
            session_state=state,
            hint_level=row["hint_level"],
            scaffold_step=row["scaffold_step"],
            is_active=row["is_active"],
            summary=row["summary"],
            total_exchanges=row["total_exchanges"]
        )

    async def get_session(self, session_id: uuid.UUID) -> Optional[Session]:
        """Get an active session by ID."""
        query = "SELECT * FROM sessions WHERE id = $1"
        row = await self._fetch_one(query, session_id)
        if not row:
            return None
            
        state = row["session_state"]
        if isinstance(state, str):
            state = json.loads(state)
            
        return Session(
            id=row["id"],
            student_id=row["student_id"],
            subject_key=row["subject_key"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            current_concept_id=row["current_concept_id"],
            current_question_id=row["current_question_id"],
            session_state=state,
            hint_level=row["hint_level"],
            scaffold_step=row["scaffold_step"],
            is_active=row["is_active"],
            summary=row["summary"],
            total_exchanges=row["total_exchanges"]
        )

    async def update_session(self, session: Session) -> None:
        """Update a session's state."""
        query = """
            UPDATE sessions 
            SET current_concept_id = $2, 
                current_question_id = $3,
                session_state = $4::jsonb,
                hint_level = $5,
                scaffold_step = $6,
                total_exchanges = $7
            WHERE id = $1
        """
        await self._execute(
            query, 
            session.id,
            session.current_concept_id,
            session.current_question_id,
            json.dumps(session.session_state),
            session.hint_level,
            session.scaffold_step,
            session.total_exchanges
        )

    async def record_attempt(self, attempt: AttemptCreate) -> uuid.UUID:
        """Log a student's answer attempt."""
        attempt_id = uuid.uuid4()
        query = """
            INSERT INTO attempts 
            (id, session_id, student_id, question_id, concept_id, 
             student_answer, is_correct, is_partial, error_type, 
             misconception_id, hint_level_used, time_taken_seconds, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
        """
        await self._execute(
            query,
            attempt_id, attempt.session_id, attempt.student_id,
            attempt.question_id, attempt.concept_id, attempt.student_answer,
            attempt.is_correct, attempt.is_partial, attempt.error_type,
            attempt.misconception_id, attempt.hint_level_used,
            attempt.time_taken_seconds
        )
        return attempt_id
