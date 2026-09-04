"""
AI Tutor — LLM Client.

Unified interface for interacting with LLM APIs (Ollama/Groq).
Includes retry logic, structured output parsing, and token logging.
"""

import json
import httpx
from typing import Type, TypeVar, Any, AsyncGenerator
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T', bound=BaseModel)


class LLMError(Exception):
    pass


class LLMClient:
    """Client for generating responses from an LLM."""
    
    def __init__(self):
        self.provider = settings.llm_provider
        
        # Determine model
        if self.provider == "ollama":
            self.model = settings.ollama_model
            self.base_url = settings.ollama_base_url
        else:
            self.model = settings.groq_model
            self.api_key = settings.groq_api_key
            self.base_url = "https://api.groq.com/openai/v1"
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_ollama(self, messages: list[dict[str, str]], json_mode: bool = False) -> str:
        """Call local Ollama API."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if json_mode:
            payload["format"] = "json"
            
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code != 200:
                logger.error("ollama_error", status_code=response.status_code, text=response.text)
                raise LLMError(f"Ollama returned {response.status_code}")
                
            data = response.json()
            return data["message"]["content"]
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _call_groq(self, messages: list[dict[str, str]], json_mode: bool = False) -> str:
        """Call Groq API (OpenAI compatible)."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error("groq_error", status_code=response.status_code, text=response.text)
                raise LLMError(f"Groq returned {response.status_code}")
                
            data = response.json()
            # Log token usage
            usage = data.get("usage", {})
            logger.info("llm_tokens", 
                        prompt_tokens=usage.get("prompt_tokens"),
                        completion_tokens=usage.get("completion_tokens"),
                        total_tokens=usage.get("total_tokens"))
                        
            return data["choices"][0]["message"]["content"]
            
    async def generate_chat(self, messages: list[dict[str, str]]) -> str:
        """Generate a natural language string from messages."""
        logger.debug("llm_chat_request", provider=self.provider, model=self.model)
        
        if self.provider == "ollama":
            return await self._call_ollama(messages)
        else:
            return await self._call_groq(messages)

    async def _call_ollama_stream(self, messages: list[dict[str, str]]) -> AsyncGenerator[str, None]:
        """Call local Ollama API with streaming."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
            
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    logger.error("ollama_stream_error", status_code=response.status_code)
                    raise LLMError(f"Ollama returned {response.status_code}")
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                    except json.JSONDecodeError:
                        continue

    async def _call_groq_stream(self, messages: list[dict[str, str]]) -> AsyncGenerator[str, None]:
        """Call Groq API with streaming."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    logger.error("groq_stream_error", status_code=response.status_code)
                    raise LLMError(f"Groq returned {response.status_code}")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line.strip() != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"] is not None:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue

    async def generate_chat_stream(self, messages: list[dict[str, str]]) -> AsyncGenerator[str, None]:
        """Generate a natural language string as a stream of tokens."""
        logger.debug("llm_stream_request", provider=self.provider, model=self.model)
        
        if self.provider == "ollama":
            async for token in self._call_ollama_stream(messages):
                yield token
        else:
            async for token in self._call_groq_stream(messages):
                yield token
            
    async def generate_structured(self, messages: list[dict[str, str]], schema: Type[T]) -> T:
        """Generate structured JSON and parse into Pydantic model."""
        logger.debug("llm_structured_request", provider=self.provider, model=self.model, schema=schema.__name__)
        
        if self.provider == "ollama":
            content = await self._call_ollama(messages, json_mode=True)
        else:
            content = await self._call_groq(messages, json_mode=True)
            
        try:
            # We strip any markdown formatting in case the model ignored json_mode slightly
            clean_content = content.strip()
            if clean_content.startswith("```json"):
                clean_content = clean_content[7:]
            if clean_content.startswith("```"):
                clean_content = clean_content[3:]
            if clean_content.endswith("```"):
                clean_content = clean_content[:-3]
                
            return schema.model_validate_json(clean_content.strip())
        except Exception as e:
            logger.error("structured_parse_error", content=content, error=str(e))
            raise LLMError("Failed to parse structured output") from e
