"""
AI Tutor — Teaching Engine.

Takes a TutorAction and contextual data, formats a prompt, 
and uses the LLMClient to generate a pedagogical Urdu response.
"""

from typing import AsyncGenerator
from app.models.enums import TutorAction
from app.tutor.llm_client import LLMClient
from app.tutor.prompt_manager import PromptManager
from app.logging import get_logger

logger = get_logger(__name__)


class TeachingEngine:
    """Generates the actual response text spoken by the AI Tutor."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.prompt_manager = PromptManager()
        

    def _build_prompt_for_action(self, action: TutorAction, context: dict, pref_lang: str) -> str:
        """Construct the prompt based on the chosen action."""
        # 1. Resolve the concept name
        concept_name = context.get("intent_data", {}).get("concept_hint", "")
        
        # If we have a current concept in context (e.g. from GREETING)
        if "current_concept" in context:
            if pref_lang == "ur":
                concept_name = context["current_concept"].get("name_ur", concept_name)
            else:
                concept_name = context["current_concept"].get("name_en", concept_name)
                
        # Override if we are teaching a prerequisite
        if action == TutorAction.TEACH_PREREQUISITE and "missing_prerequisite" in context:
            if pref_lang == "ur":
                concept_name = context["missing_prerequisite"].get("name_ur", concept_name)
            else:
                concept_name = context["missing_prerequisite"].get("name_en", concept_name)
                
        if not concept_name:
            concept_name = "math" if pref_lang == "en" else "ریاضی"

        # 2. Extract necessary variables for template interpolation
        kwargs = {
            "concept": concept_name,
            "step": context.get("session", {}).get("scaffold_step", 1),
            "question_text": "",
            "student_message": context.get("session", {}).get("student_raw_message", "")
        }
        
        # 3. Add question text if asking a question
            
        # Add question text if asking a question
        if action in [TutorAction.ASK_QUESTION, TutorAction.START_ASSESSMENT] and "question_data" in context:
            kwargs["question_text"] = context["question_data"].get("question_text", "")
            
        base_prompt = self.prompt_manager.get_action_prompt(pref_lang, action.value, **kwargs)
        
        # 4. Inject visual instructions if needed
        visual_need = "none"
        if "current_concept" in context:
            visual_need = context["current_concept"].get("visual_need", "none")
        elif "missing_prerequisite" in context:
            visual_need = context["missing_prerequisite"].get("visual_need", "none")
            
        if visual_need == "graph":
            visual_instruction = self.prompt_manager.get_action_prompt(pref_lang, "visual_instruction_graph")
            base_prompt += visual_instruction
        elif visual_need == "diagram":
            visual_instruction = self.prompt_manager.get_action_prompt(pref_lang, "visual_instruction_diagram")
            base_prompt += visual_instruction
            
        return base_prompt

    async def generate_response(self, action: TutorAction, context: dict) -> str:
        """Generate the final response string."""
        pref = context.get("session", {}).get("preferred_language", "ur")
        prompt = self._build_prompt_for_action(action, context, pref)
        
        messages = [
            {"role": "system", "content": self.prompt_manager.get_system_prompt(pref)},
            {"role": "user", "content": prompt}
        ]
        
        logger.info("teaching_engine_generating", action=action)
        response = await self.llm.generate_chat(messages)
        return response

    async def generate_response_stream(self, action: TutorAction, context: dict) -> AsyncGenerator[str, None]:
        """Generate the response string as a stream of tokens."""
        pref = context.get("session", {}).get("preferred_language", "ur")
        prompt = self._build_prompt_for_action(action, context, pref)
        
        messages = [
            {"role": "system", "content": self.prompt_manager.get_system_prompt(pref)},
            {"role": "user", "content": prompt}
        ]
        
        logger.info("teaching_engine_generating_stream", action=action)
        async for token in self.llm.generate_chat_stream(messages):
            yield token
