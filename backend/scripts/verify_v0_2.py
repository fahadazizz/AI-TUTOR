import asyncio
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.mastery_repo import MasteryRepository
from app.repositories.session_repo import SessionRepository
from app.services.session_manager import SessionManager

async def main():
    print("=== Testing V0.2 Core Loop ===")
    
    import random
    with TestClient(app) as client:
        phone = str(random.randint(1000000000, 9999999999))
        # 1. Register student
        resp = client.post("/api/auth/register", json={
            "name": "Test V0.2 Student",
            "phone": phone,
            "class_level": 10,
            "board": "punjab",
            "group_type": "science",
            "preferred_language": "en"
        })
        student_id = resp.json()["student_id"]
        print(f"Registered Student: {student_id}")
        
        # 2. Start Session
        resp = client.post("/api/auth/start-session", json={
            "student_id": student_id,
            "subject_key": "mathematics"
        })
        session_id = resp.json()["session_id"]
        print(f"Started Session: {session_id}")
        
        # 3. Ask to teach a concept
        print("\n[Student] Teach me quadratic equations")
        resp = client.post("/api/chat", json={
            "session_id": session_id,
            "message": "teach me quadratic equations"
        })
        chat_resp = resp.json()
        print(f"[Tutor Action]: {chat_resp['action_taken']}")
        
        # Check if a question was asked
        if chat_resp["action_taken"] != "ask_question":
            print("\n[Student] I understand. Let's move on.")
            resp = client.post("/api/chat", json={
                "session_id": session_id,
                "message": "I understand. Let's move on."
            })
            chat_resp = resp.json()
            print(f"[Tutor Action]: {chat_resp['action_taken']}")
            
        # We should have a question now. Let's inspect the DB session.
        session_repo = SessionRepository()
        session_manager = SessionManager(session_repo)
        active_session = await session_manager.get_active_session(session_id)
        
        expected_ans = active_session.session_state.get("current_question_expected_answer")
        concept_id = active_session.current_concept_id
        question_id = active_session.current_question_id
        print(f"\n[Session State] Concept: {concept_id}, Question: {question_id}, Expected: {expected_ans}")
        
        if not expected_ans:
            print("Error: No expected answer found in session state.")
            return
            
        # 4. Answer the question correctly
        print(f"\n[Student] {expected_ans}")
        resp = client.post("/api/chat", json={
            "session_id": session_id,
            "message": expected_ans
        })
        chat_resp = resp.json()
        print(f"[Tutor Action]: {chat_resp['action_taken']}")
        
        # 5. Verify the Attempt and Mastery in DB
        mastery_repo = MasteryRepository()
        mastery = await mastery_repo.get_mastery(uuid.UUID(student_id), concept_id)
        
        print(f"\n=== DB Mastery Inspection ===")
        print(mastery)
        
        if mastery and mastery["mastery_state"] != "unknown":
            print("\nSUCCESS: Mastery state properly updated in DB!")
        else:
            print("\nFAILED: Mastery state was not updated.")

if __name__ == "__main__":
    asyncio.run(main())
