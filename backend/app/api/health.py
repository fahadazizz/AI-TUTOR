"""
AI Tutor — Health Check API.

Provides a health check endpoint that verifies:
1. The API server is running
2. Database connection is alive
"""

from fastapi import APIRouter

from app.db.connection import get_pool
from app.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns server status and database connectivity.
    Used by monitoring tools and load balancers.
    """
    db_status = "disconnected"

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                db_status = "connected"
    except RuntimeError:
        # Pool not initialized — app is starting up or DB not configured
        db_status = "not_initialized"
    except Exception as e:
        logger.error("health_check_db_error", error=str(e))
        db_status = f"error: {type(e).__name__}"

    return {
        "status": "ok",
        "service": "ai-tutor-backend",
        "database": db_status,
    }
