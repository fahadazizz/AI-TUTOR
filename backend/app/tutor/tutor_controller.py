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
from app.engines.pedagogy_router import PedagogyRouter
from app.engines.verifier_registry import VerifierRegistry
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
        pedagogy_router: PedagogyRouter,
        verifier_registry: VerifierRegistry,
        student_model: StudentModel,
        curriculum_model: CurriculumModel,
        question_selector: QuestionSelector
    ):
        self.pedagogy_router = pedagogy_router
        self.verifier_registry = verifier_registry
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
        
        # 1. Subject-specific pedagogical intents (Answer, Solve, Continue)
        if intent in [StudentIntent.ANSWER_QUESTION, StudentIntent.SOLVE_PROBLEM, StudentIntent.CONTINUE, StudentIntent.UNKNOWN]:
            concept_id = session_state.get("current_concept_id")
            if not concept_id:
                # If they try to answer/continue but there's no active concept
                if intent == StudentIntent.ANSWER_QUESTION:
                    return TutorAction.REDIRECT_OFFTOPIC, context, None, None
                return TutorAction.RESUME_SESSION, context, None, None
                
            concept_data = await self.curriculum.get_concept(concept_id)
            pedagogy_type = concept_data.get("pedagogy_type", "quantitative") if concept_data else "quantitative"
            
            plugin = self.pedagogy_router.get_plugin(pedagogy_type)
            
            return await plugin.decide_action(
                intent_data=intent_data,
                session_state=session_state,
                student_mastery_list=student_mastery_list,
                context=context,
                curriculum=self.curriculum,
                student_model=self.student_model,
                question_selector=self.question_selector,
                verifier_registry=self.verifier_registry
            )

        # 2. Ask Concept Flow (Generic Curriculum rule)
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
                        # Soft Prerequisite Push/Pull Logic
                        warned_for = session_state.get("warned_prereq_for")
                        if warned_for == target_concept_id:
                            # User insisted! Let them learn the target concept.
                            session_state["warned_prereq_for"] = None
                            session_state["current_concept_id"] = target_concept_id
                            session_state["current_question_id"] = None
                            session_state["current_question_expected_answer"] = None
                            context["current_concept"] = await self.curriculum.get_concept(target_concept_id)
                            return TutorAction.TEACH_CONCEPT, context, None, None
                        else:
                            # First time asking. Push them to the prerequisite.
                            first_missing = missing_prereqs[0]
                            missing_concept_data = await self.curriculum.get_concept(first_missing)
                            
                            context["missing_prerequisite"] = missing_concept_data
                            context["target_concept_id"] = target_concept_id
                            session_state["warned_prereq_for"] = target_concept_id
                            
                            # Switch their current concept to the missing prerequisite
                            session_state["current_concept_id"] = first_missing
                            session_state["current_question_id"] = None
                            session_state["current_question_expected_answer"] = None
                            context["current_concept"] = missing_concept_data
                            return TutorAction.TEACH_PREREQUISITE, context, None, None
                            
                    # Proceed to teach the target concept (no prereqs missing)
                    session_state["warned_prereq_for"] = None
                    session_state["current_concept_id"] = target_concept_id
                    session_state["current_question_id"] = None
                    session_state["current_question_expected_answer"] = None
                    context["current_concept"] = await self.curriculum.get_concept(target_concept_id)
                    return TutorAction.TEACH_CONCEPT, context, None, None

        # 3.5. Clarify Step
        elif intent == StudentIntent.CLARIFY_STEP:
            return TutorAction.CLARIFY_STEP, context, None, None
            
        # 3.6. Express Frustration
        elif intent == StudentIntent.EXPRESS_FRUSTRATION:
            return TutorAction.HANDLE_FRUSTRATION, context, None, None

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
            
        # 7. Fallback
        return TutorAction.RESUME_SESSION, context, None, None
