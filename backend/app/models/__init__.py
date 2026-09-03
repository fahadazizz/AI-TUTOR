"""
AI Tutor — Models Package.

Re-exports all model classes for convenient importing:
    from app.models import Concept, Question, Student, MasteryState
"""

from app.models.enums import (
    MasteryState,
    PedagogyType,
    Severity,
    QuestionType,
    StudentIntent,
    TutorAction,
)
from app.models.curriculum import (
    Concept,
    ConceptsFile,
    KeyTerm,
    Misconception,
    MisconceptionsFile,
    PrerequisiteEdge,
    PrerequisiteGraph,
    Question,
    QuestionsFile,
    SolutionStep,
    WorkedExample,
    WorkedExampleStep,
)
from app.models.student import Student, StudentCreate
from app.models.mastery import ConceptMastery, MasterySummary, MasteryUpdate
from app.models.session import (
    Attempt,
    AttemptCreate,
    Session,
    SessionCreate,
)

__all__ = [
    # Enums
    "MasteryState",
    "PedagogyType",
    "Severity",
    "QuestionType",
    "StudentIntent",
    "TutorAction",
    # Curriculum
    "Concept",
    "ConceptsFile",
    "KeyTerm",
    "Misconception",
    "MisconceptionsFile",
    "PrerequisiteEdge",
    "PrerequisiteGraph",
    "Question",
    "QuestionsFile",
    "SolutionStep",
    "WorkedExample",
    "WorkedExampleStep",
    # Student
    "Student",
    "StudentCreate",
    # Mastery
    "ConceptMastery",
    "MasterySummary",
    "MasteryUpdate",
    # Session
    "Attempt",
    "AttemptCreate",
    "Session",
    "SessionCreate",
]
