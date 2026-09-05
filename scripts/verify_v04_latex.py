import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.models.enums import TutorAction
from app.tutor.llm_client import LLMClient
from app.tutor.teaching_engine import TeachingEngine

async def test_llm_latex_rendering():
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
                    "explanation_ur": "The standard form is $ax^2 + bx + c = 0$."
                }
            }
        },
        {
            "action": TutorAction.SCAFFOLD_PROBLEM,
            "pref": "ur",
            "context": {
                "session": {"preferred_language": "ur"},
                "current_concept": {
                    "name_ur": "دو درجی مساوات (Quadratic Equation)",
                },
                "question_data": {
                    "question_text": "$2x^2 + 4x - 6 = 0$ کو حل کریں۔"
                }
            }
        }
    ]
    
    for idx, case in enumerate(test_cases):
        print(f"\n--- Test Case {idx+1} ({case['pref']}) ---")
        response = await engine.generate_response(case["action"], case["context"])
        print("\nLLM Output:\n")
        print(response)
        if "$" in response:
            print("\n✅ SUCCESS: LLM output contains LaTeX $ tags.")
        else:
            print("\n❌ WARNING: No $ tags found in the response. The LLM might be ignoring the system prompt.")

if __name__ == "__main__":
    asyncio.run(test_llm_latex_rendering())
