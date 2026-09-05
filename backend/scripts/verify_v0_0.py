import asyncio
import sys
import uuid
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.db.connection import create_pool, close_pool
from app.repositories.curriculum_repo import CurriculumRepository
from app.tutor.llm_client import LLMClient
from app.logging import setup_logging

async def test_db():
    print("\n[DB] Testing Database Connection...")
    try:
        await create_pool()
        repo = CurriculumRepository()
        count = await repo.get_concept_count()
        print(f"[DB] ✅ Success! Found {count} concepts in DB.")
    except Exception as e:
        print(f"[DB] ❌ Failed: {e}")
        raise
    finally:
        await close_pool()

async def test_llm():
    print(f"\n[LLM] Testing LLM Provider ({settings.llm_provider})...")
    
    # Force use Ollama as requested by the user
    settings.llm_provider = "ollama"
    
    client = LLMClient()
    try:
        # A simple greeting prompt
        messages = [{"role": "user", "content": "Say 'hello, world' and nothing else."}]
        print(f"[LLM] Sending test request to {settings.ollama_model}...")
        response = await client.generate_chat(messages=messages)
        print(f"[LLM] ✅ Success! Received response: {response}")
    except Exception as e:
        print(f"[LLM] ❌ Failed: {e}")
        raise

async def main():
    setup_logging()
    print("=== Starting V0.0 Verification ===\n")
    await test_db()
    await test_llm()
    print("\n=== V0.0 Verification Complete ===")

if __name__ == "__main__":
    asyncio.run(main())
