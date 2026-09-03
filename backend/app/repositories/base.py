"""
AI Tutor — Base Repository.

Abstract base for all repository classes. Provides the connection
pool reference and common query patterns. All database access in
the application goes through repository classes — never raw SQL
in route handlers.
"""

import asyncpg

from app.db.connection import get_pool
from app.logging import get_logger


class BaseRepository:
    """Base class providing database access for all repositories.

    Usage:
        repo = CurriculumRepository()
        concepts = await repo.get_all_concepts()
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

    async def _get_pool(self) -> asyncpg.Pool:
        """Get the database connection pool."""
        return await get_pool()

    async def _fetch_one(self, query: str, *args: object) -> asyncpg.Record | None:
        """Execute a query and return a single row."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def _fetch_all(self, query: str, *args: object) -> list[asyncpg.Record]:
        """Execute a query and return all rows."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def _execute(self, query: str, *args: object) -> str:
        """Execute a query that doesn't return rows (INSERT, UPDATE, DELETE)."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def _execute_many(self, query: str, args: list[tuple]) -> None:
        """Execute a query for many rows (batch insert)."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.executemany(query, args)
