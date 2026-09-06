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
    plugin_mock = AsyncMock()
    plugin_mock.decide_action = AsyncMock(return_value=(TutorAction.GIVE_FEEDBACK_CORRECT, {}, None, None))
    
    router_mock = MagicMock()
    router_mock.get_plugin = MagicMock(return_value=plugin_mock)
    
    verifier_mock = MagicMock()
    
    student_mock = MagicMock()
    curriculum_mock = MagicMock()
    curriculum_mock.get_concept = AsyncMock(return_value={"pedagogy_type": "quantitative"})
    curriculum_mock.resolve_concept = AsyncMock(return_value="quad_101")
    curriculum_mock.get_missing_prerequisites = AsyncMock(return_value=[])
    selector_mock = MagicMock()
    
    # We will attach the plugin mock to the router so tests can manipulate it
    router_mock.plugin_mock = plugin_mock
    
    return TutorController(router_mock, verifier_mock, student_mock, curriculum_mock, selector_mock)


@pytest.mark.asyncio
async def test_decide_action_off_topic(controller):
    intent = IntentSchema(intent=StudentIntent.OFF_TOPIC)
    action, ctx, _, _ = await controller.decide_action(intent, {}, [])
    assert action == TutorAction.REDIRECT_OFFTOPIC


@pytest.mark.asyncio
async def test_decide_action_solve_problem(controller):
    controller.pedagogy_router.plugin_mock.decide_action.return_value = (TutorAction.SCAFFOLD_PROBLEM, {}, None, None)
    
    intent = IntentSchema(intent=StudentIntent.SOLVE_PROBLEM)
    session = {"current_concept_id": "concept_1"}
    action, ctx, _, _ = await controller.decide_action(intent, session, [])
    assert action == TutorAction.SCAFFOLD_PROBLEM


@pytest.mark.asyncio
async def test_decide_action_ask_concept(controller):
    intent = IntentSchema(intent=StudentIntent.ASK_CONCEPT, concept_hint="quadratic")
    action, ctx, _, _ = await controller.decide_action(intent, {}, [])
    assert action == TutorAction.TEACH_CONCEPT


@pytest.mark.asyncio
async def test_decide_action_answer_correct(controller):
    controller.pedagogy_router.plugin_mock.decide_action.return_value = (TutorAction.GIVE_FEEDBACK_CORRECT, {}, None, None)
    
    intent = IntentSchema(intent=StudentIntent.ANSWER_QUESTION, student_answer="5")
    session = {
        "current_question_expected_answer": "5",
        "current_concept_id": "concept_1",
        "current_question_id": "q1",
        "session_id": "00000000-0000-0000-0000-000000000000",
        "student_id": "00000000-0000-0000-0000-000000000000"
    }
    
    action, ctx, _, _ = await controller.decide_action(intent, session, [])
    assert action == TutorAction.GIVE_FEEDBACK_CORRECT


@pytest.mark.asyncio
async def test_decide_action_answer_wrong_hint(controller):
    controller.pedagogy_router.plugin_mock.decide_action.return_value = (TutorAction.GIVE_HINT, {}, None, None)
    
    intent = IntentSchema(intent=StudentIntent.ANSWER_QUESTION, student_answer="4")
    session = {
        "current_question_expected_answer": "5",
        "current_concept_id": "concept_1",
        "current_question_id": "q1",
        "session_id": "00000000-0000-0000-0000-000000000000",
        "student_id": "00000000-0000-0000-0000-000000000000"
    }
    
    action, ctx, _, _ = await controller.decide_action(intent, session, [])
    assert action == TutorAction.GIVE_HINT


@pytest.mark.asyncio
async def test_decide_action_answer_wrong_sign_error(controller):
    controller.pedagogy_router.plugin_mock.decide_action.return_value = (TutorAction.DIAGNOSE_MISTAKE, {}, None, None)
    
    intent = IntentSchema(intent=StudentIntent.ANSWER_QUESTION, student_answer="-5")
    session = {
        "current_question_expected_answer": "5",
        "current_concept_id": "concept_1",
        "current_question_id": "q1",
        "session_id": "00000000-0000-0000-0000-000000000000",
        "student_id": "00000000-0000-0000-0000-000000000000"
    }
    
    action, ctx, _, _ = await controller.decide_action(intent, session, [])
    assert action == TutorAction.DIAGNOSE_MISTAKE
