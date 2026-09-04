"""
AI Tutor — Student Model.

Core logic engine for student state transitions. Decides when a student
moves between mastery states (e.g. PRACTICING -> MASTERED) based on
their answer results.
"""

from datetime import datetime, timezone

from app.core.models import AnswerResult
from app.models.enums import MasteryState
from app.models.mastery import ConceptMastery


class StudentModel:
    """Business logic for student mastery and progress."""

    def __init__(self) -> None:
        pass

    def evaluate_transition(self, current: ConceptMastery, result: AnswerResult) -> ConceptMastery:
        """Evaluate and apply state transition rules based on a new answer.
        
        Returns a newly updated ConceptMastery object (does not mutate the original).
        """
        # Create a copy for the updated state
        updated = ConceptMastery(
            student_id=current.student_id,
            concept_id=current.concept_id,
            mastery_state=current.mastery_state,
            consecutive_correct=current.consecutive_correct,
            consecutive_wrong=current.consecutive_wrong,
            total_attempts=current.total_attempts + 1,
            total_correct=current.total_correct,
            misconception_ids=current.misconception_ids.copy(),
            last_attempt_at=datetime.now(timezone.utc),
            mastered_at=current.mastered_at,
        )

        if result.is_correct:
            updated.total_correct += 1
            updated.consecutive_correct += 1
            updated.consecutive_wrong = 0
        else:
            updated.consecutive_wrong += 1
            updated.consecutive_correct = 0

        # Record misconception if detected
        if result.misconception_id and result.misconception_id not in updated.misconception_ids:
            updated.misconception_ids.append(result.misconception_id)

        # ── State Machine Transition Rules ─────────────────────────

        state = updated.mastery_state

        if state == MasteryState.UNKNOWN:
            if result.is_correct:
                updated.mastery_state = MasteryState.PARTIAL
            else:
                updated.mastery_state = MasteryState.ASSESSED_WEAK

        elif state == MasteryState.INTRODUCED:
            if result.is_correct:
                updated.mastery_state = MasteryState.PRACTICING
            else:
                # Still trying to grasp the basics
                pass 

        elif state == MasteryState.PRACTICING:
            if updated.consecutive_correct >= 3:
                updated.mastery_state = MasteryState.MASTERED
                updated.mastered_at = datetime.now(timezone.utc)
            elif updated.consecutive_wrong >= 3:
                updated.mastery_state = MasteryState.STRUGGLING

        elif state == MasteryState.STRUGGLING:
            if updated.consecutive_correct >= 2:
                # Recovered from struggling
                updated.mastery_state = MasteryState.PRACTICING

        elif state == MasteryState.PARTIAL:
            if updated.consecutive_correct >= 2:
                updated.mastery_state = MasteryState.MASTERED
                updated.mastered_at = datetime.now(timezone.utc)
            elif updated.consecutive_wrong >= 2:
                updated.mastery_state = MasteryState.STRUGGLING

        elif state == MasteryState.NEEDS_REVIEW:
            if result.is_correct:
                updated.mastery_state = MasteryState.MASTERED
            else:
                updated.mastery_state = MasteryState.PRACTICING

        elif state == MasteryState.ASSESSED_WEAK:
            # Requires teaching/remediation before they can practice
            if result.is_correct:
                updated.mastery_state = MasteryState.INTRODUCED

        return updated
