"""
AI Tutor — Curriculum Data Models.

Pydantic models for concepts, questions, misconceptions, and
prerequisite relationships. These validate the seed JSON data
and serve as the internal representation throughout the backend.
"""

from pydantic import BaseModel, Field
from typing import Optional


from app.models.enums import PedagogyType, Severity


# ── Key Term ────────────────────────────────────────

class KeyTerm(BaseModel):
    """A bilingual technical term."""

    en: str
    ur: str


# ── Worked Example Step ─────────────────────────────

class WorkedExampleStep(BaseModel):
    """A single step in a worked example."""

    step: int
    description_ur: str
    math: str
    result: str


class WorkedExample(BaseModel):
    """A complete worked example with problem and step-by-step solution."""

    problem: str
    steps: list[WorkedExampleStep]


# ── Concept ─────────────────────────────────────────

class Concept(BaseModel):
    """A single teachable concept in the curriculum.

    This is the atomic unit of the Curriculum Model. Each concept
    has a unique ID, belongs to a subject/chapter, and contains
    everything needed to teach it: explanation, formulas, key terms,
    and worked examples — all in Urdu.
    """

    concept_id: str = Field(..., description="Globally unique concept identifier")
    subject: str = Field(default="mathematics")
    chapter: int = Field(..., ge=0, description="Chapter number (0 = prerequisite)")
    chapter_name: str
    name_en: str
    name_ur: str
    difficulty: int = Field(..., ge=1, le=5)
    textbook_page: Optional[str] = None
    pedagogy_type: PedagogyType
    learning_objectives: list[str] = Field(default_factory=list)
    formulas: list[str] = Field(default_factory=list)
    explanation_ur: str
    key_terms: list[KeyTerm] = Field(default_factory=list)
    worked_examples: list[WorkedExample] = Field(default_factory=list)


# ── Prerequisite Edge ───────────────────────────────

class PrerequisiteEdge(BaseModel):
    """An edge in the prerequisite DAG.

    States that `concept_id` requires all concepts in
    `prerequisites` to be mastered before it can be taught.
    """

    concept_id: str
    prerequisites: list[str]


class PrerequisiteGraph(BaseModel):
    """The complete prerequisite graph loaded from prerequisites.json."""

    edges: list[PrerequisiteEdge]


# ── Solution Step ───────────────────────────────────

class SolutionStep(BaseModel):
    """A single step in a question's solution."""

    step: int
    description_ur: str
    math: str


# ── Question ────────────────────────────────────────

class Question(BaseModel):
    """A single question in the question bank.

    Questions are tied to concepts and have progressive difficulty
    levels (1-6). Each question includes Urdu/English text,
    expected answer, solution steps, and progressive hints.
    """

    question_id: str = Field(..., description="Globally unique question identifier")
    concept_id: str = Field(..., description="The concept this question tests")
    difficulty: int = Field(..., ge=1, le=6)
    question_type: str
    question_text_ur: str
    question_text_en: str
    expected_answer: str
    answer_tolerance: Optional[float] = None
    expected_answer_unit: Optional[str] = None
    solution_steps: list[SolutionStep] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


# ── Misconception ───────────────────────────────────

class Misconception(BaseModel):
    """A documented student misconception.

    Misconceptions are tied to specific concepts and include
    detection patterns, severity rating, remediation strategy,
    and links to diagnostic/practice questions.
    """

    misconception_id: str = Field(..., description="Globally unique misconception identifier")
    concept_id: str
    subject: str = "mathematics"
    description_en: str
    description_ur: str
    severity: Severity
    error_patterns: list[str] = Field(default_factory=list)
    prerequisite_gap: Optional[str] = None
    remediation_strategy: str
    remediation_explanation_ur: str
    diagnostic_question_ids: list[str] = Field(default_factory=list)
    practice_question_ids: list[str] = Field(default_factory=list)


# ── Collection Wrappers (for loading JSON files) ────

class ConceptsFile(BaseModel):
    """Schema for concepts.json file."""

    concepts: list[Concept]


class QuestionsFile(BaseModel):
    """Schema for question bank JSON files."""

    questions: list[Question]


class MisconceptionsFile(BaseModel):
    """Schema for misconceptions.json file."""

    misconceptions: list[Misconception]
