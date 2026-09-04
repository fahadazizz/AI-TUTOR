"""
AI Tutor — Session Manager.

Business logic for managing tutoring sessions and logging attempts.
"""

import uuid
from typing import Optional

from app.models.session import Session, SessionCreate, AttemptCreate
from app.repositories.session_repo import SessionRepository
from app.logging import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages the state of active tutoring sessions."""

    def __init__(self, repo: SessionRepository):
        self.repo = repo

    async def start_session(self, student_id: str, subject_key: str = "mathematics") -> Session:
        """Initialize a new session."""
        try:
            student_uuid = uuid.UUID(student_id)
            session_data = SessionCreate(student_id=student_uuid, subject_key=subject_key)
            session = await self.repo.create_session(session_data)
            logger.info("session_started", session_id=str(session.id), student=student_id)
            return session
        except Exception as e:
            logger.error("session_start_failed", student=student_id, error=str(e))
            raise

    async def get_active_session(self, session_id: str) -> Optional[Session]:
        """Retrieve an active session context."""
        try:
            sid = uuid.UUID(session_id)
            return await self.repo.get_session(sid)
        except Exception as e:
            logger.error("session_get_failed", session=session_id, error=str(e))
            return None

    async def update_context(self, session: Session) -> None:
        """Persist context changes."""
        await self.repo.update_session(session)
        logger.debug("session_updated", session_id=str(session.id))

    async def log_attempt(self, attempt_data: AttemptCreate) -> None:
        """Log a student's answer attempt to feed the student model later."""
        await self.repo.record_attempt(attempt_data)
