import asyncio
import httpx
import uuid
import json

async def run_evaluation():
    base_url = "http://127.0.0.1:8001/api"
    
    print("\n--- V1 SYSTEM EVALUATION RUN ---")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Register
        print("\n1. Registering new student (Roman Urdu)...")
        phone = "eval-" + str(uuid.uuid4())[:8]
        res = await client.post(f"{base_url}/auth/register", json={
            "name": "Eval Student",
            "phone": phone,
            "class_level": 10,
            "board": "punjab",
            "group_type": "science",
            "preferred_language": "roman_ur"
        })
        student_id = res.json()["student_id"]
        
        # 2. Start Session
        print("\n2. Starting Session (Mathematics)...")
        res = await client.post(f"{base_url}/auth/start-session", json={
            "student_id": student_id,
            "subject_key": "mathematics"
        })
        session_id = res.json()["session_id"]
        print(f"Session ID: {session_id}")
        
        # Helper function for chatting
        async def chat(message: str, description: str):
            print(f"\n[{description}]")
            print(f"Student: {message}")
            res = await client.post(f"{base_url}/chat", json={
                "session_id": session_id,
                "message": message
            })
            data = res.json()
            print(f"Action Taken by Controller: {data['action_taken']}")
            print(f"Tutor: {data['response']}")
            return data

        # Scenarios
        await chat("Assalam o Alaikum, mujhe quadratic formula seekhna hai", "Greeting & Intent Extraction")
        
        await chat("Formula mein minus b kyun hota hai shuru mein? Iska kya matlab hai?", "Nuance & Context Injection Test")
        
        # To test the math checker, let's pretend the tutor asked a math question. 
        # We can't guarantee what the tutor will ask, so we will send a random math answer to see how it handles an unexpected math input.
        await chat("x = 4", "Math Answer (Simulated Error/Unknown state)")
        
        # Ask to solve a problem to test scaffolding
        await chat("x^2 - 5x + 6 = 0 ko solve kar ke de dein plzz", "Solve Problem (Scaffolding Test)")
        
        print("\n--- EVALUATION COMPLETE ---\n")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
