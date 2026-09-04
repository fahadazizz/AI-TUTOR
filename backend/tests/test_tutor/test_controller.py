"""Tests for the deterministic Tutor Controller."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from app.models.enums import StudentIntent, TutorAction
from app.tutor.tutor_controller import TutorController
from app.tutor.language_layer import IntentSchema
from app.core.models import AnswerResult


@pytest.fixture
def controller():
    # Mock all the core components
    math_mock = MagicMock()
    student_mock = MagicMock()
    curriculum_mock = MagicMock()
    curriculum_mock.resolve_concept = AsyncMock(return_value="quad_101")
    curriculum_mock.get_missing_prerequisites = AsyncMock(return_value=[])
    selector_mock = MagicMock()
    
    return TutorController(math_mock, student_mock, curriculum_mock, selector_mock)


@pytest.mark.asyncio
async def test_decide_action_off_topic(controller):
    intent = IntentSchema(intent=StudentIntent.OFF_TOPIC)
    action, ctx = await controller.decide_action(intent, {}, [])
    assert action == TutorAction.REDIRECT_OFFTOPIC


@pytest.mark.asyncio
async def test_decide_action_solve_problem(controller):
    intent = IntentSchema(intent=StudentIntent.SOLVE_PROBLEM)
    action, ctx = await controller.decide_action(intent, {}, [])
    assert action == TutorAction.SCAFFOLD_PROBLEM


@pytest.mark.asyncio
async def test_decide_action_ask_concept(controller):
    intent = IntentSchema(intent=StudentIntent.ASK_CONCEPT, concept_hint="quadratic")
    action, ctx = await controller.decide_action(intent, {}, [])
    assert action == TutorAction.TEACH_CONCEPT


@pytest.mark.asyncio
async def test_decide_action_answer_correct(controller):
    controller.math_checker.check_answer.return_value = AnswerResult(is_correct=True)
    
    intent = IntentSchema(intent=StudentIntent.ANSWER_QUESTION, student_answer="5")
    session = {"current_question_expected_answer": "5"}
    
    action, ctx = await controller.decide_action(intent, session, [])
    assert action == TutorAction.GIVE_FEEDBACK_CORRECT


@pytest.mark.asyncio
async def test_decide_action_answer_wrong_hint(controller):
    controller.math_checker.check_answer.return_value = AnswerResult(is_correct=False, error_type=None)
    
    intent = IntentSchema(intent=StudentIntent.ANSWER_QUESTION, student_answer="4")
    session = {"current_question_expected_answer": "5"}
    
    action, ctx = await controller.decide_action(intent, session, [])
    assert action == TutorAction.GIVE_HINT


@pytest.mark.asyncio
async def test_decide_action_answer_wrong_sign_error(controller):
    controller.math_checker.check_answer.return_value = AnswerResult(is_correct=False, error_type="sign_error")
    
    intent = IntentSchema(intent=StudentIntent.ANSWER_QUESTION, student_answer="-5")
    session = {"current_question_expected_answer": "5"}
    
    action, ctx = await controller.decide_action(intent, session, [])
    assert action == TutorAction.DIAGNOSE_MISTAKE
