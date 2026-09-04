"""
AI Tutor — Tests for Student Model.
"""

import uuid
from datetime import datetime

from app.core.student_model import StudentModel
from app.core.models import AnswerResult
from app.models.enums import MasteryState
from app.models.mastery import ConceptMastery

student_id = uuid.uuid4()
concept_id = "c01"


def create_initial_mastery(state: MasteryState) -> ConceptMastery:
    return ConceptMastery(
        student_id=student_id,
        concept_id=concept_id,
        mastery_state=state,
    )


def test_transition_unknown_to_assessed_weak():
    model = StudentModel()
    mastery = create_initial_mastery(MasteryState.UNKNOWN)
    result = AnswerResult(is_correct=False)
    
    updated = model.evaluate_transition(mastery, result)
    assert updated.mastery_state == MasteryState.ASSESSED_WEAK
    assert updated.consecutive_wrong == 1
    assert updated.total_attempts == 1


def test_transition_practicing_to_mastered():
    model = StudentModel()
    mastery = create_initial_mastery(MasteryState.PRACTICING)
    
    # 3 correct answers
    for _ in range(3):
        mastery = model.evaluate_transition(mastery, AnswerResult(is_correct=True))
        
    assert mastery.mastery_state == MasteryState.MASTERED
    assert mastery.consecutive_correct == 3
    assert mastery.mastered_at is not None


def test_transition_practicing_to_struggling():
    model = StudentModel()
    mastery = create_initial_mastery(MasteryState.PRACTICING)
    
    # 3 wrong answers
    for _ in range(3):
        mastery = model.evaluate_transition(mastery, AnswerResult(is_correct=False))
        
    assert mastery.mastery_state == MasteryState.STRUGGLING
    assert mastery.consecutive_wrong == 3


def test_recovery_from_struggling():
    model = StudentModel()
    mastery = create_initial_mastery(MasteryState.STRUGGLING)
    
    # 2 correct answers to recover
    for _ in range(2):
        mastery = model.evaluate_transition(mastery, AnswerResult(is_correct=True))
        
    assert mastery.mastery_state == MasteryState.PRACTICING


def test_misconception_recording():
    model = StudentModel()
    mastery = create_initial_mastery(MasteryState.PRACTICING)
    
    result = AnswerResult(is_correct=False, error_type="sign_error", misconception_id="m_sign_01")
    updated = model.evaluate_transition(mastery, result)
    
    assert "m_sign_01" in updated.misconception_ids
    
    # Ensure it doesn't duplicate
    updated2 = model.evaluate_transition(updated, result)
    assert len(updated2.misconception_ids) == 1
