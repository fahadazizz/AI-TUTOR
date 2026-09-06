"""
AI Tutor — Base Pedagogy Plugin.

Defines the abstract interface for subject-specific teaching flows.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
import uuid

from app.models.enums import TutorAction
from app.models.session import AttemptCreate
from app.models.mastery import ConceptMastery
from app.tutor.language_layer import IntentSchema
from app.core.student_model import StudentModel
from app.core.curriculum_model import CurriculumModel
from app.core.question_selector import QuestionSelector
from app.engines.verifier_registry import VerifierRegistry


class PedagogyPlugin(ABC):
    """Abstract interface for a pedagogy flow (e.g. quantitative, conceptual)."""

    @abstractmethod
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
        """
        Determine the next pedagogical action based on the student's intent.
        
        Args:
            intent_data: The parsed intent.
            session_state: Current session variables.
            student_mastery_list: List of the student's mastery records.
            context: Shared context dictionary.
            curriculum: CurriculumModel for fetching data.
            student_model: StudentModel for updating state.
            question_selector: QuestionSelector for fetching next questions.
            verifier_registry: VerifierRegistry for evaluating answers.
            
        Returns:
            Tuple of (TutorAction, UpdatedContext, UpdatedMastery, AttemptRecord)
        """
        pass
