from __future__ import annotations

from tests.conftest import get_client


def test_health_check():
    client = get_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["demo_mode"] is True
    assert "groq_configured" in data
    assert "vision_available" in data


def test_root_endpoint():
    client = get_client()
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["demo_mode"] is True
