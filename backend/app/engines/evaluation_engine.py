"""
AI Tutor — Universal Evaluation Engine.

Provides a pluggable interface for checking student answers across
different subjects (Math, Physics, Biology, etc.) without hardcoding
subject-specific logic into the TutorController.
"""

from abc import ABC, abstractmethod
from app.core.models import AnswerResult
from app.logging import get_logger

logger = get_logger(__name__)


class AnswerEvaluator(ABC):
    """Base interface for all subject-specific answer checkers."""

    @abstractmethod
    def check_answer(
        self, student_input: str, expected: str, question_type: str = "procedural"
    ) -> AnswerResult:
        """Evaluate a student's answer against the expected answer."""
        pass


class EvaluationEngine:
    """Factory and router for answer evaluation plugins."""

    def __init__(self):
        self._plugins: dict[str, AnswerEvaluator] = {}
        self._register_default_plugins()

    def _register_default_plugins(self):
        """Register the built-in plugins."""
        try:
            from app.engines.plugins.math_checker import MathChecker
            self.register_plugin("mathematics", MathChecker())
        except ImportError as e:
            logger.warning(f"Could not load MathChecker plugin: {e}")

        try:
            from app.engines.plugins.text_checker import TextChecker
            self.register_plugin("text_default", TextChecker())
        except ImportError as e:
            logger.warning(f"Could not load TextChecker plugin: {e}")

    def register_plugin(self, subject: str, evaluator: AnswerEvaluator):
        """Register a new evaluator for a subject."""
        self._plugins[subject] = evaluator
        logger.debug(f"Registered evaluation plugin for {subject}")

    def evaluate(
        self, student_input: str, expected: str, subject: str, question_type: str = "procedural"
    ) -> AnswerResult:
        """Route the evaluation to the correct plugin based on subject."""
        evaluator = self._plugins.get(subject)
        
        if not evaluator:
            logger.warning(f"No specific plugin for subject '{subject}'. Using text_default fallback.")
            evaluator = self._plugins.get("text_default")
            
        if not evaluator:
            # Absolute fallback if even text_checker fails to load
            logger.error("No evaluation plugin available. Falling back to basic string match.")
            is_correct = (student_input.strip().lower() == expected.strip().lower())
            return AnswerResult(is_correct=is_correct)
            
        return evaluator.check_answer(student_input, expected, question_type)
