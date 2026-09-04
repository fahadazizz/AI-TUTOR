"""
AI Tutor — Teaching Engine.

Takes a TutorAction and contextual data, formats a prompt, 
and uses the LLMClient to generate a pedagogical Urdu response.
"""

from typing import AsyncGenerator
from app.models.enums import TutorAction
from app.tutor.llm_client import LLMClient
from app.logging import get_logger

logger = get_logger(__name__)


class TeachingEngine:
    """Generates the actual response text spoken by the AI Tutor."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.base_system = """You are an expert, friendly AI Math Tutor for a 10th-grade student in Punjab, Pakistan.
You MUST strictly speak in native Urdu script (Nastaliq/Arabic script). Do NOT use Roman Urdu or Hindi script under any circumstances.
You are extremely encouraging. You NEVER give the direct answer to a problem; you guide them.
Use simple language. Format mathematical expressions clearly using text or basic LaTeX without complex markdown if not needed.
"""

    def _build_prompt_for_action(self, action: TutorAction, context: dict) -> str:
        """Construct the prompt based on the chosen action."""
        if action == TutorAction.GIVE_FEEDBACK_CORRECT:
            return "The student just got the answer completely right! Praise them warmly in Urdu and ask if they are ready for the next question."
            
        elif action == TutorAction.GIVE_HINT:
            return "The student got the answer wrong. Give them a gentle hint in Urdu to help them think about the next step. Do NOT give them the answer."
            
        elif action == TutorAction.DIAGNOSE_MISTAKE:
            error = context.get("answer_result").error_type
            if error == "sign_error":
                return "The student made a + or - sign error. Explain in Urdu how to check their signs."
            return "The student made a specific mistake. Help them realize it in Urdu without giving the answer."
            
        elif action == TutorAction.TEACH_CONCEPT:
            concept = context.get("intent_data", {}).get("concept_hint", "this math concept")
            return f"The student wants to learn about '{concept}'. Explain the basics of this concept in very simple Urdu using a real-life analogy."
            
        elif action == TutorAction.SCAFFOLD_PROBLEM:
            step = context.get("session", {}).get("scaffold_step", 1)
            return (
                f"The student asked you to solve a problem for them. YOU MUST NOT SOLVE IT DIRECTLY. "
                f"Instead, use 'Scaffolding'. We are currently on Step {step} of solving this problem. "
                f"Break the problem down into small steps. "
                f"Ask them to perform ONLY the very next micro-step in Urdu. Wait for their answer. "
                f"For example, if it's a quadratic equation, first ask them to identify a, b, and c."
            )
            
        elif action == TutorAction.HANDLE_GREETING:
            return "The student said hello. Reply with a warm, encouraging greeting in Urdu (e.g., Walikum Assalam) and ask what math topic they'd like to work on today."
            
        elif action == TutorAction.REDIRECT_OFFTOPIC:
            return "The student is talking about something off-topic (not math). Politely guide them back to mathematics in Urdu."
            
        # Fallback
        return "Say something encouraging in Urdu to keep the session moving forward."

    async def generate_response(self, action: TutorAction, context: dict) -> str:
        """Generate the final response string."""
        prompt = self._build_prompt_for_action(action, context)
        
        messages = [
            {"role": "system", "content": self.base_system},
            {"role": "user", "content": prompt}
        ]
        
        logger.info("teaching_engine_generating", action=action)
        response = await self.llm.generate_chat(messages)
        return response

    async def generate_response_stream(self, action: TutorAction, context: dict) -> AsyncGenerator[str, None]:
        """Generate the response string as a stream of tokens."""
        prompt = self._build_prompt_for_action(action, context)
        
        messages = [
            {"role": "system", "content": self.base_system},
            {"role": "user", "content": prompt}
        ]
        
        logger.info("teaching_engine_generating_stream", action=action)
        async for token in self.llm.generate_chat_stream(messages):
            yield token
