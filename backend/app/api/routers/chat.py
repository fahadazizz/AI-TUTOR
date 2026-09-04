"""
AI Tutor — Chat Router.

The primary entry point for student interaction.
"""

import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models.enums import TutorAction
from app.tutor.llm_client import LLMClient
from app.tutor.language_layer import LanguageLayer
from app.tutor.tutor_controller import TutorController
from app.tutor.teaching_engine import TeachingEngine
from app.tutor.guardrails import Guardrails

from app.core.math_checker import MathChecker
from app.core.student_model import StudentModel
from app.core.curriculum_model import CurriculumModel
from app.core.question_selector import QuestionSelector

from app.repositories.curriculum_repo import CurriculumRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.mastery_repo import MasteryRepository
from app.repositories.student_repo import StudentRepository
from app.services.session_manager import SessionManager

from app.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    action_taken: str


# Dependency injection
def get_tutor_dependencies():
    # Setup LLM components
    llm = LLMClient()
    language = LanguageLayer(llm)
    teaching = TeachingEngine(llm)
    guardrails = Guardrails()

    # Setup core components
    curriculum_repo = CurriculumRepository()
    curriculum = CurriculumModel(curriculum_repo)
    selector = QuestionSelector(curriculum_repo)
    math_checker = MathChecker()
    student_model = StudentModel()

    controller = TutorController(math_checker, student_model, curriculum, selector)

    # Setup session
    session_repo = SessionRepository()
    session_manager = SessionManager(session_repo)
    mastery_repo = MasteryRepository()
    student_repo = StudentRepository()

    return {
        "language": language,
        "controller": controller,
        "teaching": teaching,
        "guardrails": guardrails,
        "session_manager": session_manager,
        "mastery_repo": mastery_repo,
        "student_repo": student_repo,
    }


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, deps: dict = Depends(get_tutor_dependencies)):
    """Main tutoring loop."""
    
    session_manager: SessionManager = deps["session_manager"]
    language: LanguageLayer = deps["language"]
    controller: TutorController = deps["controller"]
    teaching: TeachingEngine = deps["teaching"]
    guardrails: Guardrails = deps["guardrails"]
    mastery_repo: MasteryRepository = deps["mastery_repo"]

    # 1. Load Session
    session = await session_manager.get_active_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")

    logger.info("chat_request_received", session=request.session_id, message_len=len(request.message))

    student_repo: StudentRepository = deps["student_repo"]
    student = await student_repo.get_student(session.student_id)
    pref_lang = student.get("preferred_language", "ur") if student else "ur"

    # Convert session model to dict context for the controller
    # In a full app, we'd also load mastery here.
    session_dict = {
        "current_concept_id": session.current_concept_id,
        "current_question_id": session.current_question_id,
        "current_question_expected_answer": session.session_state.get("current_question_expected_answer"),
        "hint_level": session.hint_level,
        "scaffold_step": session.scaffold_step,
        "preferred_language": pref_lang,
        "student_raw_message": request.message
    }

    # 2. Detect Intent
    intent_data = await language.detect_intent(request.message)

    # 3. Controller Decide Action
    # Fetch real mastery
    mastery_list = await mastery_repo.get_all_mastery(session.student_id)
    action, updated_context = await controller.decide_action(intent_data, session_dict, mastery_list)

    # 4. Generate Response with Guardrails
    max_retries = 3
    final_response = None
    
    for attempt in range(max_retries):
        response_text = await teaching.generate_response(action, updated_context)
        gr_result = guardrails.check_response(response_text, updated_context)
        
        if gr_result.passed:
            final_response = response_text
            break
        else:
            logger.warning("guardrail_retry", attempt=attempt+1, reason=gr_result.reason)
            
    if not final_response:
        # Fallback if guardrails continually fail
        logger.error("guardrail_total_failure")
        final_response = "Mujhe maaf kijiye, mujhe samajh nahi aaya. Kya aap dobara pooch sakte hain?"
        action = TutorAction.RESUME_SESSION

    # 5. Save state
    session.total_exchanges += 1
    # Update fields from the context if they changed
    # (Simplified for now, in a real app we'd map context changes back to session)
    await session_manager.update_context(session)

    return ChatResponse(response=final_response, action_taken=action.value)

@router.post("/stream")
async def chat_stream_endpoint(request: ChatRequest, deps: dict = Depends(get_tutor_dependencies)):
    """Streaming tutoring loop."""
    
    session_manager: SessionManager = deps["session_manager"]
    language: LanguageLayer = deps["language"]
    controller: TutorController = deps["controller"]
    teaching: TeachingEngine = deps["teaching"]
    guardrails: Guardrails = deps["guardrails"]
    mastery_repo: MasteryRepository = deps["mastery_repo"]

    # 1. Load Session
    session = await session_manager.get_active_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")

    logger.info("chat_stream_request_received", session=request.session_id, message_len=len(request.message))

    student_repo: StudentRepository = deps["student_repo"]
    student = await student_repo.get_student(session.student_id)
    pref_lang = student.get("preferred_language", "ur") if student else "ur"

    session_dict = {
        "current_concept_id": session.current_concept_id,
        "current_question_id": session.current_question_id,
        "current_question_expected_answer": session.session_state.get("current_question_expected_answer"),
        "hint_level": session.hint_level,
        "scaffold_step": session.scaffold_step,
        "preferred_language": pref_lang,
        "student_raw_message": request.message
    }

    # 2. Detect Intent
    intent_data = await language.detect_intent(request.message)

    # 3. Controller Decide Action
    mastery_list = await mastery_repo.get_all_mastery(session.student_id)
    action, updated_context = await controller.decide_action(intent_data, session_dict, mastery_list)

    async def generate_sse():
        # Yield metadata first (action taken)
        meta_event = json.dumps({"type": "meta", "action_taken": action.value})
        yield f"data: {meta_event}\n\n"
        
        accumulated_text = ""
        # Yield tokens
        async for token in teaching.generate_response_stream(action, updated_context):
            accumulated_text += token
            
            # Apply guardrails to the accumulating stream
            gr_result = guardrails.check_response(accumulated_text, updated_context)
            if not gr_result.passed:
                logger.warning("streaming_guardrail_failed", reason=gr_result.reason)
                # Yield a fallback token to overwrite or inform the user
                fallback_chunk = json.dumps({"type": "token", "content": "\n\n[System] Mera system is waqt jawab dene se qasir hai. Hum doosra sawaal karte hain."})
                yield f"data: {fallback_chunk}\n\n"
                break

            # Send each token
            chunk = json.dumps({"type": "token", "content": token})
            yield f"data: {chunk}\n\n"
            
        # 5. Save state after streaming
        session.total_exchanges += 1
        await session_manager.update_context(session)
        
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_sse(), media_type="text/event-stream")
