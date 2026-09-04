"""
AI Tutor — Guardrails.

Validates the LLM's response before sending it to the user.
"""

from dataclasses import dataclass
from typing import Optional

from app.logging import get_logger

logger = get_logger(__name__)


@dataclass
class GuardrailResult:
    passed: bool
    reason: Optional[str] = None


class Guardrails:
    """Safety checks for AI Tutor responses."""
    
    def check_response(self, response_text: str, context: dict) -> GuardrailResult:
        """Run all guardrails on the response text."""
        
        # 1. Length check
        if len(response_text) > 800:
            logger.warning("guardrail_failed_length", length=len(response_text))
            return GuardrailResult(False, "Response is too long (over 800 chars).")
            
        # 2. Answer Leak Check
        expected_ans = context.get("session", {}).get("current_question_expected_answer")
        if expected_ans:
            # Simple substring check (can be improved)
            # If expected answer is "4", and text has " 4 ", it might be a leak.
            # We'll just check if the exact string is in the text for now,
            # but only for somewhat unique strings to avoid false positives.
            if len(str(expected_ans)) > 1 and str(expected_ans) in response_text:
                logger.warning("guardrail_failed_leak", expected=expected_ans)
                return GuardrailResult(False, "Response leaked the exact expected answer.")
                
        # 3. Language Drift (Very simple heuristic)
        # Check for Devanagari script (Hindi) which is a common failure mode
        for char in response_text:
            if '\u0900' <= char <= '\u097F':
                logger.warning("guardrail_failed_language_drift_hindi")
                return GuardrailResult(False, "Response contains Hindi script instead of Urdu.")
                
        return GuardrailResult(True)
