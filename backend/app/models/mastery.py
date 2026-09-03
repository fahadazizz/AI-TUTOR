"""
AI Tutor — Mastery Data Models.

Tracks a student's mastery state for each concept.
The update logic implements the state machine defined
in the architecture document (Section 3.3).
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import MasteryState


class ConceptMastery(BaseModel):
    """A student's mastery record for a single concept.

    This is the core of the Student Model. The `state` field
    drives the Tutor Controller's decisions about what to teach.
    """

    student_id: uuid.UUID
    concept_id: str
    mastery_state: MasteryState = MasteryState.UNKNOWN
    consecutive_correct: int = Field(default=0, ge=0)
    consecutive_wrong: int = Field(default=0, ge=0)
    total_attempts: int = Field(default=0, ge=0)
    total_correct: int = Field(default=0, ge=0)
    last_attempt_at: Optional[datetime] = None
    mastered_at: Optional[datetime] = None
    misconception_ids: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.now)


class MasteryUpdate(BaseModel):
    """Payload for updating a student's mastery after an attempt."""

    student_id: uuid.UUID
    concept_id: str
    is_correct: bool
    is_partial: bool = False
    misconception_id: Optional[str] = None


class MasterySummary(BaseModel):
    """Summary of a student's mastery across all concepts in a subject."""

    student_id: uuid.UUID
    subject: str
    total_concepts: int
    mastered: int
    practicing: int
    struggling: int
    unknown: int
    concepts: list[ConceptMastery]
