"""
AI Tutor — Text Answer Checking Engine.

A basic checker for non-mathematical subjects. In the future, this can be
upgraded to use a fast, constrained LLM call for semantic equivalence.
"""

import re
from app.core.models import AnswerResult
from app.engines.evaluation_engine import AnswerEvaluator
from app.logging import get_logger

logger = get_logger(__name__)


class TextChecker(AnswerEvaluator):
    """Basic text equivalence verification."""

    def __init__(self) -> None:
        pass

    def sanitize_input(self, text: str) -> str:
        """Clean and normalize text input."""
        if not text:
            return ""
        # Lowercase and remove extra whitespace/punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def check_answer(
        self, student_input: str, expected: str, question_type: str = "conceptual"
    ) -> AnswerResult:
        """Evaluate a student's text answer."""
        clean_student = self.sanitize_input(student_input)
        clean_expected = self.sanitize_input(expected)

        if not clean_student or not clean_expected:
            return AnswerResult(is_correct=False)

        # Exact match
        if clean_student == clean_expected:
            return AnswerResult(is_correct=True)

        # Partial/Substring match (very basic semantic check)
        # If the expected keywords are found in the student's answer
        expected_words = set(clean_expected.split())
        student_words = set(clean_student.split())
        
        # If all expected words are in the student's answer (e.g. expected: "cell membrane", student: "it is the cell membrane")
        if expected_words.issubset(student_words):
            return AnswerResult(is_correct=True)

        # If at least half the expected words are there, count as partial
        if len(expected_words) > 0:
            overlap = expected_words.intersection(student_words)
            if len(overlap) / len(expected_words) >= 0.5:
                return AnswerResult(
                    is_correct=False,
                    is_partial=True,
                    error_type="incomplete_concept",
                    feedback_hint="آپ کا جواب کچھ حد تک درست ہے، لیکن مکمل نہیں۔ کیا آپ مزید وضاحت کر سکتے ہیں؟"
                )

        return AnswerResult(is_correct=False)
