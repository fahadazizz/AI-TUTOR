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
