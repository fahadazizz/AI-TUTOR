"""
AI Tutor — Session & Attempt Data Models.

Sessions track a tutoring conversation. Attempts log
individual question interactions within a session.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Session(BaseModel):
    """A tutoring session between a student and the AI tutor.

    Sessions persist across reconnects. The session_state JSONB
    holds transient controller data (e.g., scaffold step, parked concept).
    """

    id: uuid.UUID
    student_id: uuid.UUID
    subject_key: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    current_concept_id: Optional[str] = None
    current_question_id: Optional[str] = None
    session_state: dict = Field(default_factory=dict)
    hint_level: int = Field(default=0, ge=0, le=3)
    scaffold_step: int = Field(default=0, ge=0)
    is_active: bool = True
    summary: Optional[str] = None
    total_exchanges: int = Field(default=0, ge=0)


class SessionCreate(BaseModel):
    """Schema for starting a new tutoring session."""

    student_id: uuid.UUID
    subject_key: str = "mathematics"


class Attempt(BaseModel):
    """A single question attempt within a session.

    Every time a student answers a question, an Attempt is recorded.
    This is the raw data that feeds the Student Model's mastery updates.
    """

    id: uuid.UUID
    session_id: uuid.UUID
    student_id: uuid.UUID
    question_id: str
    concept_id: str
    student_answer: str
    is_correct: bool
    is_partial: bool = False
    error_type: Optional[str] = None
    misconception_id: Optional[str] = None
    hint_level_used: int = Field(default=0, ge=0)
    time_taken_seconds: Optional[int] = None
    created_at: datetime


class AttemptCreate(BaseModel):
    """Schema for recording a new question attempt."""

    session_id: uuid.UUID
    student_id: uuid.UUID
    question_id: str
    concept_id: str
    student_answer: str
    is_correct: bool
    is_partial: bool = False
    error_type: Optional[str] = None
    misconception_id: Optional[str] = None
    hint_level_used: int = 0
    time_taken_seconds: Optional[int] = None
