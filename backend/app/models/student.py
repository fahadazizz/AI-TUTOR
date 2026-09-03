"""
AI Tutor — Student Data Models.

Pydantic models for student profiles. Students are identified
by UUID and have minimal required fields (name + phone).
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    """Schema for creating a new student."""

    name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=20)
    class_level: int = Field(default=10, ge=1, le=12)
    board: str = Field(default="punjab")
    group_type: str = Field(default="science")
    preferred_language: str = Field(default="ur")


class Student(BaseModel):
    """A registered student with all profile data."""

    id: uuid.UUID
    name: str
    phone: Optional[str] = None
    class_level: int = 10
    board: str = "punjab"
    group_type: str = "science"
    preferred_language: str = "ur"
    created_at: datetime
