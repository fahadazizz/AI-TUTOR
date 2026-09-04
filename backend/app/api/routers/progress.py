"""
AI Tutor — Progress Router.

Endpoints for viewing student mastery and progress.
"""

from fastapi import APIRouter, HTTPException, Depends

from app.repositories.mastery_repo import MasteryRepository
from app.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/progress", tags=["progress"])

def get_progress_deps():
    return {"mastery_repo": MasteryRepository()}


@router.get("/{student_id}")
async def get_student_progress(student_id: str, deps: dict = Depends(get_progress_deps)):
    """Get overall progress for a student across all subjects."""
    repo: MasteryRepository = deps["mastery_repo"]
    try:
        mastery = await repo.get_student_mastery(student_id)
        return {"student_id": student_id, "mastery": mastery}
    except Exception as e:
        logger.error("get_progress_failed", student_id=student_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch progress")


@router.get("/{student_id}/{concept_id}")
async def get_concept_progress(student_id: str, concept_id: str, deps: dict = Depends(get_progress_deps)):
    """Get mastery for a specific concept."""
    repo: MasteryRepository = deps["mastery_repo"]
    try:
        mastery = await repo.get_concept_mastery(student_id, concept_id)
        if not mastery:
            raise HTTPException(status_code=404, detail="No progress for this concept")
        return mastery
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_concept_progress_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch concept progress")
