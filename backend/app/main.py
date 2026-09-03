"""
AI Tutor Backend — FastAPI Application Entry Point.

This is the main application factory. It creates the FastAPI app,
configures lifespan events (startup/shutdown), and registers routers.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging import setup_logging, get_logger
from app.db.connection import create_pool, close_pool, run_migrations
from app.api.health import router as health_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager.

    Startup:
      1. Configure structured logging
      2. Create database connection pool
      3. Run pending database migrations

    Shutdown:
      1. Close database connection pool
    """
    # ── Startup ─────────────────────────────────────
    setup_logging()
    logger.info(
        "app_starting",
        env=settings.app_env,
        llm_provider=settings.llm_provider,
    )

    try:
        await create_pool()
        await run_migrations()
        logger.info("app_ready")
    except Exception as e:
        logger.error("startup_failed", error=str(e))
        # App still starts — health endpoint will report DB as disconnected
        # This allows the server to run even without DB for development

    yield

    # ── Shutdown ────────────────────────────────────
    await close_pool()
    logger.info("app_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="AI Tutor API",
        description="AI-powered Urdu/English tutor for Class 10 (Punjab Board)",
        version="0.1.0",
        lifespan=lifespan,
    )

    # ── CORS ────────────────────────────────────────
    # Allow frontend (Next.js) to call the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",   # Next.js dev server
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ─────────────────────────────────────
    app.include_router(health_router)

    return app


# The app instance — used by uvicorn
app = create_app()
