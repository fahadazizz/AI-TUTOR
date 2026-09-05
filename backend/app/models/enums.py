"""
AI Tutor — Enumeration Types.

Centralized enums used throughout the system. These match the
architecture document's state machine definitions exactly.
"""

from enum import Enum


class MasteryState(str, Enum):
    """Student's mastery level for a specific concept.

    Transition rules (from architecture doc):
      UNKNOWN  → ASSESSED_WEAK  (initial assessment shows weakness)
      UNKNOWN  → PRACTICING     (initial assessment shows ok)
      UNKNOWN  → INTRODUCED     (concept has been explained)
      INTRODUCED → PRACTICING   (first correct answer)
      PRACTICING → MASTERED     (3 consecutive correct)
      PRACTICING → STRUGGLING   (3 consecutive wrong)
      STRUGGLING → PRACTICING   (1 correct answer)
      MASTERED → NEEDS_REVIEW   (1 wrong answer)
      NEEDS_REVIEW → MASTERED   (correct on review)
      NEEDS_REVIEW → STRUGGLING (wrong on review)
    """

    UNKNOWN = "unknown"
    ASSESSED_WEAK = "assessed_weak"
    INTRODUCED = "introduced"
    PRACTICING = "practicing"
    STRUGGLING = "struggling"
    PARTIAL = "partial"
    MASTERED = "mastered"
    NEEDS_REVIEW = "needs_review"


class PedagogyType(str, Enum):
    """How a concept should be taught."""

    CONCEPTUAL = "conceptual"    # Understanding-based (what and why)
    PROCEDURAL = "procedural"    # Step-by-step method (how)
    APPLICATION = "application"  # Real-world problem solving


class Severity(str, Enum):
    """Severity of a misconception."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QuestionType(str, Enum):
    """Type of question in the question bank."""

    RECOGNITION = "recognition"
    IDENTIFICATION = "identification"
    PROCEDURAL = "procedural"
    APPLICATION = "application"
    WORD_PROBLEM = "word_problem"
    BOARD_STYLE = "board_style"
    CHALLENGE = "challenge"


class StudentIntent(str, Enum):
    """Classified intent from the Language Layer."""

    ASK_CONCEPT = "ask_concept"
    ANSWER_QUESTION = "answer_question"
    SOLVE_PROBLEM = "solve_problem"
    GREETING = "greeting"
    OFF_TOPIC = "off_topic"
    CONTINUE = "continue"
    REPEAT = "repeat"
    CHANGE_SUBJECT = "change_subject"
    REVIEW = "review"
    EXPRESS_FRUSTRATION = "express_frustration"
    UNKNOWN = "unknown"


class TutorAction(str, Enum):
    """Action the Tutor Controller decides to take."""

    TEACH_CONCEPT = "teach_concept"
    ASK_QUESTION = "ask_question"
    GIVE_HINT = "give_hint"
    DIAGNOSE_MISTAKE = "diagnose_mistake"
    GIVE_FEEDBACK_CORRECT = "give_feedback_correct"
    GIVE_FEEDBACK_PARTIAL = "give_feedback_partial"
    TEACH_PREREQUISITE = "teach_prerequisite"
    SCAFFOLD_PROBLEM = "scaffold_problem"
    START_ASSESSMENT = "start_assessment"
    HANDLE_GREETING = "handle_greeting"
    REDIRECT_OFFTOPIC = "redirect_offtopic"
    HANDLE_FRUSTRATION = "handle_frustration"
    RESUME_SESSION = "resume_session"
