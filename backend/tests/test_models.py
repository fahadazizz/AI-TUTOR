"""
AI Tutor — Pydantic Model Validation Tests.

These tests verify that our Pydantic models correctly validate
the actual seed JSON data files. If any JSON structure doesn't
match the models, these tests will catch it.
"""

import json
from pathlib import Path

import pytest

from app.models.curriculum import (
    Concept,
    ConceptsFile,
    Misconception,
    MisconceptionsFile,
    PrerequisiteGraph,
    Question,
    QuestionsFile,
)
from app.models.enums import MasteryState, PedagogyType, Severity
from app.models.mastery import ConceptMastery, MasteryUpdate
from app.models.student import Student, StudentCreate
from app.models.session import Session, SessionCreate, Attempt, AttemptCreate

# ── Path to seed data ───────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "curriculum" / "mathematics"


def load_json(filepath: Path) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# ════════════════════════════════════════════════════
# Concept Validation
# ════════════════════════════════════════════════════

class TestConceptModels:
    """Validate that concepts.json parses into our Concept model."""

    def test_concepts_file_loads_successfully(self):
        """The entire concepts.json file should parse without errors."""
        data = load_json(DATA_DIR / "concepts.json")
        file_model = ConceptsFile(**data)
        assert len(file_model.concepts) > 0

    def test_all_concepts_have_required_fields(self):
        """Every concept must have concept_id, name_en, name_ur, explanation_ur."""
        data = load_json(DATA_DIR / "concepts.json")
        for raw in data["concepts"]:
            concept = Concept(**raw)
            assert concept.concept_id, f"Missing concept_id"
            assert concept.name_en, f"Missing name_en for {concept.concept_id}"
            assert concept.name_ur, f"Missing name_ur for {concept.concept_id}"
            assert concept.explanation_ur, f"Missing explanation_ur for {concept.concept_id}"

    def test_concept_ids_are_unique(self):
        """No duplicate concept IDs."""
        data = load_json(DATA_DIR / "concepts.json")
        ids = [c["concept_id"] for c in data["concepts"]]
        assert len(ids) == len(set(ids)), f"Duplicate concept IDs found: {[x for x in ids if ids.count(x) > 1]}"

    def test_concept_difficulty_range(self):
        """Difficulty must be between 1 and 5."""
        data = load_json(DATA_DIR / "concepts.json")
        for raw in data["concepts"]:
            concept = Concept(**raw)
            assert 1 <= concept.difficulty <= 5, (
                f"Concept {concept.concept_id} has invalid difficulty {concept.difficulty}"
            )

    def test_pedagogy_type_is_valid_enum(self):
        """pedagogy_type must be one of: conceptual, procedural, application."""
        data = load_json(DATA_DIR / "concepts.json")
        for raw in data["concepts"]:
            concept = Concept(**raw)
            assert concept.pedagogy_type in PedagogyType, (
                f"Concept {concept.concept_id} has invalid pedagogy_type: {concept.pedagogy_type}"
            )

    def test_concept_count_matches_expected(self):
        """We should have at least 14 concepts (7 prereqs + 7 chapter 2)."""
        data = load_json(DATA_DIR / "concepts.json")
        file_model = ConceptsFile(**data)
        assert len(file_model.concepts) >= 14


# ════════════════════════════════════════════════════
# Prerequisite Graph Validation
# ════════════════════════════════════════════════════

class TestPrerequisiteModels:
    """Validate prerequisites.json against the PrerequisiteGraph model."""

    def test_prerequisites_file_loads_successfully(self):
        data = load_json(DATA_DIR / "prerequisites.json")
        graph = PrerequisiteGraph(**data)
        assert len(graph.edges) > 0

    def test_no_self_referencing_prerequisites(self):
        """A concept cannot be a prerequisite of itself."""
        data = load_json(DATA_DIR / "prerequisites.json")
        graph = PrerequisiteGraph(**data)
        for edge in graph.edges:
            assert edge.concept_id not in edge.prerequisites, (
                f"Self-reference: {edge.concept_id} lists itself as prerequisite"
            )

    def test_all_prerequisite_concepts_exist(self):
        """Every concept and prerequisite referenced must exist in concepts.json."""
        concepts_data = load_json(DATA_DIR / "concepts.json")
        valid_ids = {c["concept_id"] for c in concepts_data["concepts"]}

        prereq_data = load_json(DATA_DIR / "prerequisites.json")
        graph = PrerequisiteGraph(**prereq_data)

        for edge in graph.edges:
            assert edge.concept_id in valid_ids, (
                f"Concept {edge.concept_id} in prerequisites not found in concepts.json"
            )
            for prereq in edge.prerequisites:
                assert prereq in valid_ids, (
                    f"Prerequisite {prereq} for {edge.concept_id} not found in concepts.json"
                )


# ════════════════════════════════════════════════════
# Question Validation
# ════════════════════════════════════════════════════

class TestQuestionModels:
    """Validate question bank JSON files against the Question model."""

    def _load_all_questions(self) -> list[Question]:
        """Load questions from all JSON files in the questions directory."""
        questions_dir = DATA_DIR / "questions"
        all_questions = []
        for qfile in sorted(questions_dir.glob("*.json")):
            data = load_json(qfile)
            file_model = QuestionsFile(**data)
            all_questions.extend(file_model.questions)
        return all_questions

    def test_all_question_files_load_successfully(self):
        questions = self._load_all_questions()
        assert len(questions) > 0

    def test_question_ids_are_unique(self):
        """No duplicate question IDs across all question files."""
        questions = self._load_all_questions()
        ids = [q.question_id for q in questions]
        assert len(ids) == len(set(ids)), f"Duplicate question IDs found"

    def test_question_difficulty_range(self):
        """Question difficulty must be between 1 and 6."""
        questions = self._load_all_questions()
        for q in questions:
            assert 1 <= q.difficulty <= 6, (
                f"Question {q.question_id} has invalid difficulty {q.difficulty}"
            )

    def test_questions_reference_valid_concepts(self):
        """Every question's concept_id must exist in concepts.json."""
        concepts_data = load_json(DATA_DIR / "concepts.json")
        valid_ids = {c["concept_id"] for c in concepts_data["concepts"]}

        questions = self._load_all_questions()
        for q in questions:
            assert q.concept_id in valid_ids, (
                f"Question {q.question_id} references unknown concept {q.concept_id}"
            )

    def test_all_questions_have_expected_answer(self):
        """Every question must have a non-empty expected_answer."""
        questions = self._load_all_questions()
        for q in questions:
            assert q.expected_answer, (
                f"Question {q.question_id} has empty expected_answer"
            )

    def test_total_question_count_meets_minimum(self):
        """We need at least 50 questions for a meaningful pilot."""
        questions = self._load_all_questions()
        assert len(questions) >= 50, (
            f"Only {len(questions)} questions. Need at least 50 for pilot."
        )


# ════════════════════════════════════════════════════
# Misconception Validation
# ════════════════════════════════════════════════════

class TestMisconceptionModels:
    """Validate misconceptions.json against the Misconception model."""

    def test_misconceptions_file_loads_successfully(self):
        data = load_json(DATA_DIR / "misconceptions.json")
        file_model = MisconceptionsFile(**data)
        assert len(file_model.misconceptions) > 0

    def test_misconception_ids_are_unique(self):
        data = load_json(DATA_DIR / "misconceptions.json")
        file_model = MisconceptionsFile(**data)
        ids = [m.misconception_id for m in file_model.misconceptions]
        assert len(ids) == len(set(ids)), "Duplicate misconception IDs found"

    def test_severity_is_valid_enum(self):
        data = load_json(DATA_DIR / "misconceptions.json")
        file_model = MisconceptionsFile(**data)
        for m in file_model.misconceptions:
            assert m.severity in Severity, (
                f"Misconception {m.misconception_id} has invalid severity: {m.severity}"
            )


# ════════════════════════════════════════════════════
# Enum Validation
# ════════════════════════════════════════════════════

class TestEnums:
    """Verify enum definitions match the architecture document."""

    def test_mastery_state_has_all_8_states(self):
        assert len(MasteryState) == 8

    def test_mastery_state_values(self):
        expected = {
            "unknown", "assessed_weak", "introduced", "practicing",
            "struggling", "partial", "mastered", "needs_review",
        }
        actual = {state.value for state in MasteryState}
        assert actual == expected


# ════════════════════════════════════════════════════
# Student Model Validation
# ════════════════════════════════════════════════════

class TestStudentModels:

    def test_student_create_with_minimal_fields(self):
        student = StudentCreate(name="Fatima")
        assert student.name == "Fatima"
        assert student.class_level == 10
        assert student.board == "punjab"

    def test_student_create_rejects_empty_name(self):
        with pytest.raises(Exception):
            StudentCreate(name="")

    def test_student_create_with_phone(self):
        student = StudentCreate(name="Ahmed", phone="03001234567")
        assert student.phone == "03001234567"
