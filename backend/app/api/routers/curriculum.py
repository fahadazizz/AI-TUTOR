"""
AI Tutor — Curriculum Router.

Endpoints for fetching questions and curriculum data.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.repositories.curriculum_repo import CurriculumRepository
from app.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])

def get_curriculum_deps():
    return {"curriculum_repo": CurriculumRepository()}


@router.get("/assessment")
async def get_assessment(deps: dict = Depends(get_curriculum_deps)):
    """Fetch the diagnostic assessment questions."""
    repo: CurriculumRepository = deps["curriculum_repo"]
    try:
        questions = await repo.get_assessment_questions(limit=15)
        # Parse the JSON string fields back to objects for the API response
        import json
        for q in questions:
            for field in ["solution_steps", "hints", "tags"]:
                if isinstance(q.get(field), str):
                    q[field] = json.loads(q[field])
        return {"questions": questions}
    except Exception as e:
        logger.error("get_assessment_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch assessment.")

@router.get("/graph/{subject_id}")
async def get_curriculum_graph(subject_id: str, deps: dict = Depends(get_curriculum_deps)):
    """Fetch the full concept graph for a given subject."""
    repo: CurriculumRepository = deps["curriculum_repo"]
    # We can instantiate CurriculumModel here locally since it's just a light wrapper
    from app.core.curriculum_model import CurriculumModel
    model = CurriculumModel(repo)
    try:
        graph = await model.get_graph(subject_id)
        return graph
    except Exception as e:
        logger.error("get_curriculum_graph_failed", subject_id=subject_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch curriculum graph.")

from app.api.routers.assessment_models import AssessmentSubmitRequest
from app.repositories.mastery_repo import MasteryRepository
from datetime import datetime

@router.post("/assessment/submit")
async def submit_assessment(
    request: AssessmentSubmitRequest, 
    deps: dict = Depends(get_curriculum_deps)
):
    """Submit diagnostic assessment answers and initialize student mastery."""
    mastery_repo = MasteryRepository()
    repo: CurriculumRepository = deps["curriculum_repo"]
    
    try:
        # Fetch all questions to compare answers
        db_questions = await repo.get_assessment_questions(limit=50)
        q_map = {q["question_id"]: q["expected_answer"] for q in db_questions}
        
        for ans in request.answers:
            expected = q_map.get(ans.question_id)
            if not expected:
                continue
                
            # Simple string match for diagnostic (ignoring case/spaces)
            is_correct = str(ans.student_answer).strip().lower() == str(expected).strip().lower()
            
            mastery_state = "mastered" if is_correct else "struggling"
            
            await mastery_repo.upsert_mastery(
                student_id=request.student_id,
                concept_id=ans.concept_id,
                mastery_state=mastery_state,
                consecutive_correct=1 if is_correct else 0,
                consecutive_wrong=0 if is_correct else 1,
                total_attempts=1,
                total_correct=1 if is_correct else 0,
                last_attempt_at=datetime.utcnow(),
                mastered_at=datetime.utcnow() if is_correct else None,
                misconception_ids=[]
            )
            
        return {"status": "success", "message": "Assessment graded and mastery updated."}
    except Exception as e:
        logger.error("submit_assessment_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process assessment.")
