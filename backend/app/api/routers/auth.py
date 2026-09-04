"""
AI Tutor — Auth Router.

Endpoints for student registration and starting sessions.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.models.student import StudentCreate
from app.repositories.student_repo import StudentRepository
from app.services.session_manager import SessionManager
from app.repositories.session_repo import SessionRepository
from app.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    phone_number: str

class StartSessionRequest(BaseModel):
    student_id: str
    subject_key: str = "mathematics"


def get_auth_deps():
    student_repo = StudentRepository()
    session_repo = SessionRepository()
    session_manager = SessionManager(session_repo)
    return {
        "student_repo": student_repo,
        "session_manager": session_manager
    }


@router.post("/register")
async def register(student: StudentCreate, deps: dict = Depends(get_auth_deps)):
    """Register a new student."""
    repo: StudentRepository = deps["student_repo"]
    try:
        new_student = await repo.create_student(
            name=student.name,
            phone=student.phone,
            class_level=student.class_level,
            board=student.board,
            group_type=student.group_type,
            preferred_language=student.preferred_language
        )
        return {"student_id": new_student["id"], "name": new_student["name"]}
    except Exception as e:
        logger.error("registration_failed", error=str(e))
        raise HTTPException(status_code=400, detail="Registration failed.")


@router.post("/login")
async def login(req: LoginRequest, deps: dict = Depends(get_auth_deps)):
    """Login a student via phone number."""
    repo: StudentRepository = deps["student_repo"]
    student = await repo.get_student_by_phone(req.phone_number)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return {"student_id": student.id, "name": student.name}


@router.post("/start-session")
async def start_session(req: StartSessionRequest, deps: dict = Depends(get_auth_deps)):
    """Start a new tutoring session."""
    manager: SessionManager = deps["session_manager"]
    session = await manager.start_session(req.student_id, req.subject_key)
    return {"session_id": session.id, "started_at": session.started_at}
