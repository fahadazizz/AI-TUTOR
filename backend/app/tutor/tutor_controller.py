"""
AI Tutor — Tutor Controller.

The pure deterministic "brain" of the system. Routes intents to actions
and updates state using the core models. Contains NO LLM logic.
"""

from typing import Dict, Any

from app.models.enums import StudentIntent, TutorAction, MasteryState
from app.core.math_checker import MathChecker
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
    ) -> tuple[TutorAction, Dict[str, Any]]:
        """
        Decide the next action based on intent and current state.
        
        Args:
            intent_data: The parsed intent from Language Layer.
            session_state: Dict holding current_concept_id, current_question_id, etc.
            student_mastery_list: List of ConceptMastery objects for this student.
            
        Returns:
            Tuple of (TutorAction, ContextDictForTeachingEngine)
        """
        intent = intent_data.intent
        context = {"intent_data": intent_data.model_dump(), "session": session_state}
        
        # 1. Answer Question Flow
        if intent == StudentIntent.ANSWER_QUESTION:
            if not session_state.get("current_question_expected_answer"):
                # They gave an answer but we didn't ask a question
                return TutorAction.REDIRECT_OFFTOPIC, context
                
            student_ans = intent_data.student_answer or ""
            expected_ans = session_state["current_question_expected_answer"]
            
            # Check answer
            result = self.math_checker.check_answer(student_ans, expected_ans)
            context["answer_result"] = result
            
            if result.is_correct:
                # To really update state we'd call StudentModel here and save to DB
                # For this controller logic, we just return the action
                return TutorAction.GIVE_FEEDBACK_CORRECT, context
            else:
                if result.error_type in ["sign_error", "incomplete_solution"]:
                    return TutorAction.DIAGNOSE_MISTAKE, context
                else:
                    return TutorAction.GIVE_HINT, context

        # 2. Ask Concept Flow
        elif intent == StudentIntent.ASK_CONCEPT:
            concept_hint = intent_data.concept_hint
            if concept_hint:
                target_concept_id = await self.curriculum.resolve_concept(concept_hint)
                if target_concept_id:
                    # Get mastered concept IDs from the mastery list
                    # Currently student_mastery_list is just a list of Mastery dicts/objects
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
                        return TutorAction.TEACH_PREREQUISITE, context
                        
                    # All prerequisites met, proceed to teach
                    session_state["current_concept_id"] = target_concept_id

            return TutorAction.TEACH_CONCEPT, context

        # 3. Solve Problem (Scaffolding rule)
        elif intent == StudentIntent.SOLVE_PROBLEM:
            # We never solve it directly
            return TutorAction.SCAFFOLD_PROBLEM, context

        # 4. Off Topic
        elif intent == StudentIntent.OFF_TOPIC:
            return TutorAction.REDIRECT_OFFTOPIC, context
            
        # 5. Greeting
        elif intent == StudentIntent.GREETING:
            return TutorAction.HANDLE_GREETING, context
            
        # 6. Fallback
        return TutorAction.RESUME_SESSION, context
