"""
AI Tutor — Quantitative Science Pedagogy Plugin.

Handles the teaching flow for math and numerical physics/chemistry.
"""

from typing import Dict, Any, Tuple, Optional
import uuid

from app.models.enums import TutorAction, MasteryState, StudentIntent
from app.models.session import AttemptCreate
from app.models.mastery import ConceptMastery
from app.tutor.language_layer import IntentSchema
from app.core.student_model import StudentModel
from app.core.curriculum_model import CurriculumModel
from app.core.question_selector import QuestionSelector
from app.engines.verifier_registry import VerifierRegistry
from app.engines.plugins.base_plugin import PedagogyPlugin


class QuantitativePlugin(PedagogyPlugin):
    """
    Teaching flow for quantitative subjects.
    
    Flow: Worked Example -> Guided Problem -> Independent Problem -> Mastery
    Verifies answers using the symbolic verifier.
    """
    
    async def decide_action(
        self,
        intent_data: IntentSchema,
        session_state: Dict[str, Any],
        student_mastery_list: list[Any],
        context: Dict[str, Any],
        curriculum: CurriculumModel,
        student_model: StudentModel,
        question_selector: QuestionSelector,
        verifier_registry: VerifierRegistry
    ) -> Tuple[TutorAction, Dict[str, Any], Optional[ConceptMastery], Optional[AttemptCreate]]:
        
        intent = intent_data.intent
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
            
            # Fetch the question to get the misconception_map
            question_data = await curriculum.get_question(question_id)
            misconception_map = question_data.get("misconception_map", {}) if question_data else {}
            
            # Check answer using symbolic verifier
            result = verifier_registry.check_answer(
                "symbolic", student_ans, expected_ans, misconception_map=misconception_map
            )
            context["answer_result"] = result
            
            # Update Student Model
            current_mastery = get_mastery(concept_id)
            updated_mastery = student_model.evaluate_transition(current_mastery, result)
            
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
                
                if result.error_type == "parse_error":
                    return TutorAction.CLARIFY_SYNTAX, context, updated_mastery, attempt
                    
                if result.error_type == "known_misconception" and result.misconception_id:
                    misconception = await curriculum.get_misconception(result.misconception_id)
                    if misconception:
                        lang = session_state.get("preferred_language", "ur")
                        explanation = misconception.get(f"remediation_explanation_{lang}")
                        if not explanation:
                            explanation = misconception.get("remediation_explanation_ur", "")
                        context["remediation_explanation"] = explanation
                        return TutorAction.REMEDIATE_MISCONCEPTION, context, updated_mastery, attempt
                
                if result.error_type in ["sign_error", "incomplete_solution"]:
                    return TutorAction.DIAGNOSE_MISTAKE, context, updated_mastery, attempt
                else:
                    return TutorAction.GIVE_HINT, context, updated_mastery, attempt

        # 2. Solve Problem (Scaffolding vs Worked Example rule)
        elif intent == StudentIntent.SOLVE_PROBLEM:
            current_hint_level = session_state.get("hint_level", 0)
            if current_hint_level >= 2:
                session_state["hint_level"] = 0
                return TutorAction.PROVIDE_WORKED_EXAMPLE, context, None, None
            else:
                return TutorAction.SCAFFOLD_PROBLEM, context, None, None

        # 3. Continue / Unknown (Trigger next question)
        elif intent in [StudentIntent.CONTINUE, StudentIntent.UNKNOWN]:
            concept_id = session_state.get("current_concept_id")
            if concept_id:
                mastery = get_mastery(concept_id)
                question = await question_selector.select_next_question(concept_id, mastery, set())
                
                if question:
                    session_state["current_question_id"] = question["question_id"]
                    session_state["current_question_expected_answer"] = question["expected_answer"]
                    session_state["hint_level"] = 0
                    context["question_data"] = question
                    return TutorAction.ASK_QUESTION, context, None, None

        # Fallback if the plugin doesn't know what to do
        return TutorAction.RESUME_SESSION, context, None, None
