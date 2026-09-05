"""
AI Tutor — Tutor Controller.

The pure deterministic "brain" of the system. Routes intents to actions
and updates state using the core models. Contains NO LLM logic.
"""

from typing import Dict, Any, Tuple, Optional
import uuid

from app.models.enums import StudentIntent, TutorAction, MasteryState
from app.models.session import AttemptCreate
from app.models.mastery import ConceptMastery
from app.engines.plugins.math_checker import MathChecker
from app.core.student_model import StudentModel
from app.core.curriculum_model import CurriculumModel
from app.core.question_selector import QuestionSelector
from app.tutor.language_layer import IntentSchema
from app.logging import get_logger

logger = get_logger(__name__)


class TutorController:
    """Deterministic routing and decision engine."""
    
    def __init__(
        self,
        math_checker: MathChecker,
        student_model: StudentModel,
        curriculum_model: CurriculumModel,
        question_selector: QuestionSelector
    ):
        self.math_checker = math_checker
        self.student_model = student_model
        self.curriculum = curriculum_model
        self.question_selector = question_selector

    async def decide_action(
        self,
        intent_data: IntentSchema,
        session_state: Dict[str, Any],
        student_mastery_list: list[Any]
    ) -> Tuple[TutorAction, Dict[str, Any], Optional[ConceptMastery], Optional[AttemptCreate]]:
        """
        Decide the next action based on intent and current state.
        
        Args:
            intent_data: The parsed intent from Language Layer.
            session_state: Dict holding current_concept_id, current_question_id, etc.
            student_mastery_list: List of ConceptMastery objects for this student.
            
        Returns:
            Tuple of (TutorAction, ContextDictForTeachingEngine, UpdatedMastery, Attempt)
        """
        intent = intent_data.intent
        context = {"intent_data": intent_data.model_dump(), "session": session_state}
        updated_mastery = None
        attempt = None
        
        # Helper to find current mastery
        def get_mastery(concept_id: str) -> ConceptMastery:
            for m in student_mastery_list:
                if isinstance(m, dict) and m.get("concept_id") == concept_id:
                    return ConceptMastery(**m)
                elif hasattr(m, "concept_id") and m.concept_id == concept_id:
                    return m
            # Return a default UNKNOWN mastery if none exists
            student_id_str = session_state.get("student_id")
            s_id = uuid.UUID(student_id_str) if student_id_str else uuid.uuid4()
            return ConceptMastery(student_id=s_id, concept_id=concept_id, mastery_state=MasteryState.UNKNOWN)
        
        # 1. Answer Question Flow
        if intent == StudentIntent.ANSWER_QUESTION:
            concept_id = session_state.get("current_concept_id")
            question_id = session_state.get("current_question_id")
            expected_ans = session_state.get("current_question_expected_answer")
            
            if not expected_ans or not concept_id or not question_id:
                # They gave an answer but we didn't ask a question
                return TutorAction.REDIRECT_OFFTOPIC, context, None, None
                
            student_ans = intent_data.student_answer or ""
            
            # Check answer
            result = self.math_checker.check_answer(student_ans, expected_ans)
            context["answer_result"] = result
            
            # Update Student Model
            current_mastery = get_mastery(concept_id)
            updated_mastery = self.student_model.evaluate_transition(current_mastery, result)
            
            # Create Attempt Record
            attempt = AttemptCreate(
                session_id=uuid.UUID(session_state["session_id"]),
                student_id=uuid.UUID(session_state["student_id"]),
                question_id=question_id,
                concept_id=concept_id,
                student_answer=student_ans,
                is_correct=result.is_correct,
                is_partial=result.is_partial,
                error_type=result.error_type,
                misconception_id=result.misconception_id,
                hint_level_used=session_state.get("hint_level", 0)
            )
            
            if result.is_correct:
                session_state["current_question_id"] = None
                session_state["current_question_expected_answer"] = None
                session_state["hint_level"] = 0
                return TutorAction.GIVE_FEEDBACK_CORRECT, context, updated_mastery, attempt
            else:
                session_state["hint_level"] = session_state.get("hint_level", 0) + 1
                if result.error_type in ["sign_error", "incomplete_solution"]:
                    return TutorAction.DIAGNOSE_MISTAKE, context, updated_mastery, attempt
                else:
                    return TutorAction.GIVE_HINT, context, updated_mastery, attempt

        # 2. Ask Concept Flow
        elif intent == StudentIntent.ASK_CONCEPT:
            concept_hint = intent_data.concept_hint
            if concept_hint:
                target_concept_id = await self.curriculum.resolve_concept(concept_hint)
                if target_concept_id:
                    # Get mastered concept IDs from the mastery list
                    mastered_ids = {
                        m["concept_id"] if isinstance(m, dict) else getattr(m, "concept_id", "")
                        for m in student_mastery_list
                        if (isinstance(m, dict) and m.get("mastery_state") == MasteryState.MASTERED.value) or
                           (hasattr(m, "mastery_state") and m.mastery_state == MasteryState.MASTERED)
                    }
                    
                    missing_prereqs = await self.curriculum.get_missing_prerequisites(target_concept_id, mastered_ids)
                    
                    if missing_prereqs:
                        # Found a missing prerequisite! Pivot to teaching the deepest missing one.
                        first_missing = missing_prereqs[0]
                        missing_concept_data = await self.curriculum.get_concept(first_missing)
                        
                        context["missing_prerequisite"] = missing_concept_data
                        context["target_concept_id"] = target_concept_id
                        
                        # We change the session to point to this new prerequisite
                        session_state["current_concept_id"] = first_missing
                        session_state["current_question_id"] = None
                        session_state["current_question_expected_answer"] = None
                        return TutorAction.TEACH_PREREQUISITE, context, None, None
                        
                    # All prerequisites met, proceed to teach
                    session_state["current_concept_id"] = target_concept_id
                    session_state["current_question_id"] = None
                    session_state["current_question_expected_answer"] = None

            return TutorAction.TEACH_CONCEPT, context, None, None

        # 3. Solve Problem (Scaffolding rule)
        elif intent == StudentIntent.SOLVE_PROBLEM:
            # We never solve it directly
            return TutorAction.SCAFFOLD_PROBLEM, context, None, None

        # 4. Off Topic
        elif intent == StudentIntent.OFF_TOPIC:
            return TutorAction.REDIRECT_OFFTOPIC, context, None, None
            
        # 5. Greeting
        elif intent == StudentIntent.GREETING:
            # Check if we have a current concept
            if session_state.get("current_concept_id"):
                concept_data = await self.curriculum.get_concept(session_state["current_concept_id"])
                context["current_concept"] = concept_data
            return TutorAction.HANDLE_GREETING, context, None, None
            
        # 6. Continue / Unknown (Trigger next question)
        elif intent in [StudentIntent.CONTINUE, StudentIntent.UNKNOWN]:
            concept_id = session_state.get("current_concept_id")
            if concept_id:
                # Find mastery for this concept
                mastery = get_mastery(concept_id)
                
                # We don't have a history of seen questions in the basic MVP context yet
                question = await self.question_selector.select_next_question(concept_id, mastery, set())
                
                if question:
                    session_state["current_question_id"] = question["question_id"]
                    session_state["current_question_expected_answer"] = question["expected_answer"]
                    session_state["hint_level"] = 0
                    context["question_data"] = question
                    return TutorAction.ASK_QUESTION, context, None, None

        # 7. Fallback
        return TutorAction.RESUME_SESSION, context, None, None
