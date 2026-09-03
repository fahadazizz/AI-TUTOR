"""
AI Tutor — Student Repository.

Database access layer for student profiles.
"""

import uuid
from datetime import datetime

from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository):
    """Repository for student data."""

    async def create_student(
        self,
        name: str,
        phone: str | None = None,
        class_level: int = 10,
        board: str = "punjab",
        group_type: str = "science",
        preferred_language: str = "ur",
    ) -> dict:
        """Create a new student and return the full record."""
        row = await self._fetch_one(
            """
            INSERT INTO students (name, phone, class_level, board, group_type, preferred_language)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """,
            name, phone, class_level, board, group_type, preferred_language,
        )
        return dict(row) if row else {}

    async def get_student(self, student_id: uuid.UUID) -> dict | None:
        """Fetch a student by ID."""
        row = await self._fetch_one(
            "SELECT * FROM students WHERE id = $1", student_id
        )
        return dict(row) if row else None

    async def get_student_by_phone(self, phone: str) -> dict | None:
        """Fetch a student by phone number."""
        row = await self._fetch_one(
            "SELECT * FROM students WHERE phone = $1", phone
        )
        return dict(row) if row else None

    async def get_student_count(self) -> int:
        """Count total students."""
        row = await self._fetch_one("SELECT COUNT(*) as cnt FROM students")
        return row["cnt"] if row else 0
