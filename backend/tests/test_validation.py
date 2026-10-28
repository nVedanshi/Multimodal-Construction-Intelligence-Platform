from __future__ import annotations

from tests.conftest import get_client


def test_planning_missing_required_field():
    client = get_client()
    response = client.post("/api/planning/project", json={})
    assert response.status_code in (400, 422)
    body = response.json()
    assert body["success"] is False


def test_valuation_negative_area():
    client = get_client()
    response = client.post(
        "/api/valuation/property",
        json={
            "city": "Pune",
            "locality": "Kothrud",
            "property_type": "residential",
            "area_value": -10,
            "area_unit": "sqft",
            "condition": "good",
        },
    )
    assert response.status_code in (400, 422)
    body = response.json()
    assert body["success"] is False


def test_knowledge_empty_message():
    client = get_client()
    response = client.post("/api/knowledge/ask", json={"message": ""})
    assert response.status_code in (400, 422)
    body = response.json()
    assert body["success"] is False
