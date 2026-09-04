"""
AI Tutor — Prompt Manager.

Loads and caches structured prompts from the data/prompts directory.
"""

import os
import json
from app.logging import get_logger

logger = get_logger(__name__)

class PromptManager:
    """Manages localized system and action prompts."""
    
    def __init__(self, prompts_dir: str = "../data/prompts"):
        self.prompts_dir = prompts_dir
        self.cache = {}
        self._load_prompts()
        
    def _load_prompts(self):
        """Load all prompts into memory."""
        for lang in ["en", "ur", "roman_ur"]:
            lang_dir = os.path.join(self.prompts_dir, lang)
            if not os.path.exists(lang_dir):
                logger.warning("prompt_dir_missing", lang=lang)
                continue
                
            # Load system.txt
            system_path = os.path.join(lang_dir, "system.txt")
            if os.path.exists(system_path):
                with open(system_path, "r", encoding="utf-8") as f:
                    system_text = f.read()
            else:
                system_text = "You are an AI Tutor."
                
            # Load actions.json
            actions_path = os.path.join(lang_dir, "actions.json")
            if os.path.exists(actions_path):
                with open(actions_path, "r", encoding="utf-8") as f:
                    actions_dict = json.load(f)
            else:
                actions_dict = {}
                
            self.cache[lang] = {
                "system": system_text,
                "actions": actions_dict
            }
            logger.info("prompts_loaded", lang=lang)

    def get_system_prompt(self, language: str) -> str:
        """Get the localized system prompt."""
        if language not in self.cache:
            language = "ur" # fallback
        return self.cache.get(language, {}).get("system", "")

    def get_action_prompt(self, language: str, action: str, **kwargs) -> str:
        """Get the localized action prompt and interpolate kwargs."""
        if language not in self.cache:
            language = "ur"
            
        actions = self.cache.get(language, {}).get("actions", {})
        template = actions.get(action.lower(), f"Say something encouraging. Action was {action}")
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error("prompt_format_error", template=template, missing_key=str(e))
            return template
