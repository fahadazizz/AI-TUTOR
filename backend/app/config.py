"""
AI Tutor Backend — Application Configuration.

Loads all environment variables using pydantic-settings.
Never hardcode API keys, database URLs, or sensitive values.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "debug"

    # ── Database ────────────────────────────────────
    database_url: str = "postgresql://postgres:postgres@localhost:54322/postgres"

    # ── LLM Provider ────────────────────────────────
    llm_provider: Literal["groq", "ollama"] = "ollama"

    # ── Groq (Cloud) ────────────────────────────────
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # ── Ollama (Local) ──────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


# Singleton instance — import this everywhere
settings = Settings()
