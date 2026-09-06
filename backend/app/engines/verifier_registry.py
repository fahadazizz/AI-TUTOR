"""
AI Tutor — Verifier Registry.

Provides a pluggable interface for checking student answers across
different verification strategies (symbolic, rubric, step-based) without hardcoding
subject-specific logic into the Pedagogy Plugins.
"""

from abc import ABC, abstractmethod
from app.core.models import AnswerResult
from app.logging import get_logger

logger = get_logger(__name__)


class BaseVerifier(ABC):
    """Base interface for all answer verifiers."""

    @abstractmethod
    def check_answer(
        self, student_input: str, expected: str, **kwargs
    ) -> AnswerResult:
        """Evaluate a student's answer against the expected answer."""
        pass


class VerifierRegistry:
    """Registry for answer verifiers (e.g. symbolic, rubric)."""

    def __init__(self):
        self._verifiers: dict[str, BaseVerifier] = {}
        self._register_default_plugins()

    def _register_default_plugins(self):
        """Register the built-in plugins."""
        try:
            from app.engines.plugins.math_checker import MathChecker
            self.register_verifier("symbolic", MathChecker())
        except ImportError as e:
            logger.warning(f"Could not load MathChecker plugin: {e}")

        try:
            from app.engines.plugins.text_checker import TextChecker
            self.register_verifier("text_default", TextChecker())
        except ImportError as e:
            logger.warning(f"Could not load TextChecker plugin: {e}")

    def register_verifier(self, verifier_type: str, verifier: BaseVerifier):
        """Register a new verifier."""
        self._verifiers[verifier_type] = verifier
        logger.debug(f"Registered verifier for {verifier_type}")

    def evaluate(
        self, student_input: str, expected: str, verifier_type: str, **kwargs
    ) -> AnswerResult:
        """Route the evaluation to the correct verifier."""
        verifier = self._verifiers.get(verifier_type)
        
        if not verifier:
            logger.warning(f"No specific verifier for type '{verifier_type}'. Using text_default fallback.")
            verifier = self._verifiers.get("text_default")
            
        if not verifier:
            # Absolute fallback if even text_checker fails to load
            logger.error("No verifier available. Falling back to basic string match.")
            is_correct = (student_input.strip().lower() == expected.strip().lower())
            return AnswerResult(is_correct=is_correct)
            
        return verifier.check_answer(student_input, expected, **kwargs)
