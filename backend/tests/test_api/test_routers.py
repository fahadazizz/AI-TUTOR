"""
Tests for API routers.
These tests use FastAPI's TestClient to verify HTTP mechanics (status codes, payloads).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Create a synchronous test client
client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_chat_requires_session_id():
    response = client.post("/api/chat", json={"message": "hello"})
    assert response.status_code == 422  # Unprocessable Entity (validation error)
    
def test_start_session_validation():
    response = client.post("/api/auth/start-session", json={})
    assert response.status_code == 422
