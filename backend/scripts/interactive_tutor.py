"""
AI Tutor — Interactive CLI Test.

This script wires up the Language Layer, Tutor Controller, Teaching Engine, 
and Guardrails to allow testing the system end-to-end via the terminal.
"""

import sys
import asyncio
from typing import Dict, Any

from app.tutor.llm_client import LLMClient
from app.tutor.language_layer import LanguageLayer
from app.tutor.tutor_controller import TutorController
from app.tutor.teaching_engine import TeachingEngine
from app.tutor.guardrails import Guardrails

from app.core.math_checker import MathChecker
from app.core.student_model import StudentModel
from app.core.curriculum_model import CurriculumModel
from app.core.question_selector import QuestionSelector

# For a mock repository without needing Postgres running just for the CLI test
class MockCurriculumRepo:
    async def get_concept_count(self): return 1
    async def get_concepts_by_subject(self, s): return []
    async def get_prerequisites(self, c): return []
    async def get_questions_by_concept(self, c): return []

async def main():
    print("=======================================")
    print("   AI Tutor Interactive CLI Session    ")
    print("=======================================")
    print("Initializing components...")
    
    # 1. Initialize API Clients
    try:
        llm = LLMClient()
    except Exception as e:
        print(f"Failed to initialize LLM Client: {e}")
        return

    # 2. Initialize Core Engines
    math_checker = MathChecker()
    student_model = StudentModel()
    mock_repo = MockCurriculumRepo()
    curriculum = CurriculumModel(mock_repo)
    selector = QuestionSelector(mock_repo)

    # 3. Initialize Tutor Engines
    language = LanguageLayer(llm)
    controller = TutorController(math_checker, student_model, curriculum, selector)
    teaching = TeachingEngine(llm)
    guardrails = Guardrails()

    print(f"Ready! Using LLM Provider: {llm.provider}")
    print("Type 'quit' or 'exit' to end the session.")
    print("---------------------------------------")

    # Mock Session State
    session_state: Dict[str, Any] = {
        "current_question_expected_answer": "4"  # Let's pretend we asked a question where answer is 4
    }

    while True:
        try:
            user_input = input("\nStudent: ")
            if user_input.lower() in ("quit", "exit"):
                break
                
            if not user_input.strip():
                continue

            print("\n[Thinking...]")
            
            # Step 1: Detect Intent
            intent_data = await language.detect_intent(user_input)
            print(f"  > Intent Detected: {intent_data.intent.value} | Hint: {intent_data.concept_hint} | Ans: {intent_data.student_answer}")

            # Step 2: Controller decides action
            action, context = await controller.decide_action(intent_data, session_state, [])
            print(f"  > Controller decided action: {action.value}")

            # Step 3: Teaching engine generates response
            response = await teaching.generate_response(action, context)
            
            # Step 4: Guardrails check
            gr_result = guardrails.check_response(response, context)
            if not gr_result.passed:
                print(f"  > Guardrail Blocked Response: {gr_result.reason}")
                print(f"Tutor (Blocked): {response}")
                continue

            print(f"\nTutor: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(main())
