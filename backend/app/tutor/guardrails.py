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


import re

class Guardrails:
    """Safety checks for AI Tutor responses."""
    
    def check_response(self, response_text: str, context: dict) -> GuardrailResult:
        """Run all guardrails on the response text."""
        
        # 1. Length check
        if len(response_text) > 4000:
            logger.warning("guardrail_failed_length", length=len(response_text))
            return GuardrailResult(False, "Response is too long (over 4000 chars).")
            
        # 2. Answer Leak Check
        expected_ans = context.get("session", {}).get("current_question_expected_answer")
        if expected_ans:
            # Use regex to check for whole word/number match to avoid false positives (e.g. "14" containing "4")
            pattern = r'\b' + re.escape(str(expected_ans)) + r'\b'
            if re.search(pattern, response_text):
                logger.warning("guardrail_failed_leak", expected=expected_ans)
                return GuardrailResult(False, "Response leaked the exact expected answer.")
                
        return GuardrailResult(True)
