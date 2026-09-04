"""
AI Tutor — Language Layer.

Translates human text (Urdu/English) into a deterministic StudentIntent.
"""

from pydantic import BaseModel, Field

from app.models.enums import StudentIntent
from app.tutor.llm_client import LLMClient
from app.logging import get_logger

logger = get_logger(__name__)


class IntentSchema(BaseModel):
    """The structured output expected from the LLM for intent detection."""
    intent: StudentIntent = Field(description="The classified intent of the user's message.")
    concept_hint: str | None = Field(default=None, description="The mathematical concept they are asking about (if intent is ASK_CONCEPT).")
    student_answer: str | None = Field(default=None, description="The numerical/algebraic answer they provided (if intent is ANSWER_QUESTION).")


class LanguageLayer:
    """Parses raw text into intents."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.system_prompt = """
You are the semantic parser for an AI Math Tutor.
Your job is to read the student's message (which could be in Urdu, Roman Urdu, or English) and classify their intent exactly.

Available intents:
- ask_concept: Asking to learn or explain a topic. (e.g., "quadratic equation kya hai?", "explain factorization")
- answer_question: Providing an answer to a math problem. (e.g., "x = 4", "answer is 5")
- solve_problem: Asking YOU to solve a problem for them. (e.g., "solve x^2 + 5x + 6 = 0")
- greeting: Saying hello. (e.g., "assalam o alaikum", "hi")
- off_topic: Talking about something unrelated to math or the current session.
- continue: Agreeing to move forward. (e.g., "yes", "theek hai", "next")
- repeat: Asking to repeat or re-explain. (e.g., "samajh nahi aya", "dobara batayein")
- change_subject: Asking to learn something else entirely.
- review: Asking to review old material.

If they provide an answer, extract the raw mathematical part into 'student_answer' (e.g., if they say "i think x = 4", student_answer="x=4").
If they ask about a concept, extract the concept name into 'concept_hint' in English (e.g., if they say "factors bananay sikha do", concept_hint="factorization").

You MUST return valid JSON matching the schema.
"""

    async def detect_intent(self, message: str) -> IntentSchema:
        """Detect the intent from a user message."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Student says: \"{message}\"\nAnalyze this and output JSON."}
        ]
        
        try:
            result = await self.llm.generate_structured(messages, IntentSchema)
            logger.info("intent_detected", intent=result.intent, concept=result.concept_hint, answer=result.student_answer)
            return result
        except Exception as e:
            logger.error("intent_detection_failed", error=str(e))
            # Fallback
            return IntentSchema(intent=StudentIntent.UNKNOWN)
