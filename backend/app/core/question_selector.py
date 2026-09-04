"""
AI Tutor — Question Selection Engine.

Determines the optimal next question for a student based on their
current mastery state and past attempts.
"""

import random

from app.repositories.curriculum_repo import CurriculumRepository
from app.models.enums import MasteryState
from app.models.mastery import ConceptMastery
from app.logging import get_logger

logger = get_logger(__name__)


class QuestionSelector:
    """Business logic for picking the next question."""

    def __init__(self, repo: CurriculumRepository) -> None:
        self.repo = repo

    def _determine_target_difficulty(self, mastery: ConceptMastery | None) -> int:
        """Decide what difficulty level (1-6) the student needs right now."""
        if not mastery or mastery.mastery_state == MasteryState.UNKNOWN:
            return 2
            
        state = mastery.mastery_state
        
        if state == MasteryState.ASSESSED_WEAK:
            return 1
        elif state == MasteryState.INTRODUCED:
            return 1
        elif state == MasteryState.STRUGGLING:
            # Drop them down to rebuild confidence
            return 1
        elif state == MasteryState.PARTIAL:
            return 2
        elif state == MasteryState.PRACTICING:
            # Escalate difficulty based on consecutive correct
            return min(4, 2 + mastery.consecutive_correct)
        elif state in (MasteryState.MASTERED, MasteryState.NEEDS_REVIEW):
            # Give them board-style or advanced questions
            return random.choice([4, 5, 6])
            
        return 2

    async def select_next_question(
        self, 
        concept_id: str, 
        mastery: ConceptMastery | None, 
        seen_question_ids: set[str]
    ) -> dict | None:
        """Select the best question for the student.
        
        Args:
            concept_id: The concept they are learning.
            mastery: Their current mastery state for this concept.
            seen_question_ids: Set of question IDs they have already attempted.
            
        Returns:
            The question dict, or None if no questions exist for this concept.
        """
        questions = await self.repo.get_questions_by_concept(concept_id)
        if not questions:
            return None
            
        target_diff = self._determine_target_difficulty(mastery)
        
        # Filter out seen questions unless we've seen them all
        unseen = [q for q in questions if q["question_id"] not in seen_question_ids]
        pool = unseen if unseen else questions
        
        # Try to find an exact difficulty match
        exact_match = [q for q in pool if q["difficulty"] == target_diff]
        if exact_match:
            return random.choice(exact_match)
            
        # Fallback: find the closest difficulty
        pool.sort(key=lambda q: abs(q["difficulty"] - target_diff))
        return pool[0]
