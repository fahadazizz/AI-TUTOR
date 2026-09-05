import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.models.enums import TutorAction
from app.tutor.llm_client import LLMClient
from app.tutor.teaching_engine import TeachingEngine

async def test_llm_visuals():
    llm = LLMClient()
    engine = TeachingEngine(llm)
    
    test_cases = [
        {
            "action": TutorAction.TEACH_CONCEPT,
            "pref": "en",
            "context": {
                "session": {"preferred_language": "en"},
                "current_concept": {
                    "name_en": "Quadratic Equation Standard Form",
                    "visual_need": "graph"
                }
            }
        },
        {
            "action": TutorAction.TEACH_CONCEPT,
            "pref": "en",
            "context": {
                "session": {"preferred_language": "en"},
                "current_concept": {
                    "name_en": "Completing the Square",
                    "visual_need": "diagram"
                }
            }
        }
    ]
    
    for idx, case in enumerate(test_cases):
        print(f"\n--- Test Case {idx+1} ({case['pref']}) ---")
        response = await engine.generate_response(case["action"], case["context"])
        print("\nLLM Output:\n")
        print(response)
        if "[Graph" in response or "[Diagram" in response:
            print("\n✅ SUCCESS: LLM output contains Visual shortcode.")
        else:
            print("\n❌ WARNING: No Visual shortcode found.")

if __name__ == "__main__":
    asyncio.run(test_llm_visuals())
