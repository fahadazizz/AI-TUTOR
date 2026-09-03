"""
AI Tutor — Health Endpoint Test.

Tests the /health endpoint without requiring a database connection.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint_returns_200():
    """Health endpoint should always return 200, even without DB."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-tutor-backend"
    assert "database" in data


@pytest.mark.asyncio
async def test_health_endpoint_reports_service_name():
    """Health response must include the correct service name."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.json()["service"] == "ai-tutor-backend"
