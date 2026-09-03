"""
AI Tutor — Database Connection Manager.

Manages an asyncpg connection pool for direct PostgreSQL access.
This gives us true async database operations, proper connection
pooling, and works with both local Supabase and cloud Supabase.
"""

import asyncpg
from pathlib import Path

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

# Module-level pool reference
_pool: asyncpg.Pool | None = None

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def create_pool() -> asyncpg.Pool:
    """Create and return the database connection pool.

    Called once during application startup (FastAPI lifespan).
    """
    global _pool
    if _pool is not None:
        return _pool

    logger.info("creating_db_pool", database_url=settings.database_url[:30] + "...")
    _pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )
    logger.info("db_pool_created")
    return _pool


async def close_pool() -> None:
    """Close the database connection pool.

    Called during application shutdown.
    """
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("db_pool_closed")


async def get_pool() -> asyncpg.Pool:
    """Get the current connection pool.

    Raises RuntimeError if the pool hasn't been created yet.
    """
    if _pool is None:
        raise RuntimeError(
            "Database pool not initialized. "
            "Ensure create_pool() is called during app startup."
        )
    return _pool


async def run_migrations() -> None:
    """Execute all SQL migration files in order.

    Reads .sql files from the migrations directory and executes
    them sequentially. Migrations are idempotent (use IF NOT EXISTS).
    """
    pool = await get_pool()

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_files:
        logger.warning("no_migrations_found", path=str(MIGRATIONS_DIR))
        return

    async with pool.acquire() as conn:
        for migration_file in migration_files:
            logger.info("running_migration", file=migration_file.name)
            sql = migration_file.read_text(encoding="utf-8")
            await conn.execute(sql)
            logger.info("migration_complete", file=migration_file.name)
