from __future__ import annotations

from tests.conftest import get_client


def test_demo_planning_returns_schema():
    client = get_client()
    response = client.post(
        "/api/planning/project",
        json={
            "project_name": "Demo Villa",
            "location": "Mumbai",
            "construction_type": "residential",
            "intended_use": "house",
            "num_floors": 2,
            "plot_area": 300,
            "plot_area_unit": "sqm",
            "built_up_area": 200,
            "built_up_area_unit": "sqm",
            "quality_level": "medium",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["meta"]["mode"] == "demo"
    data = body["data"]
    assert "total_estimated_cost_inr" in data
    assert isinstance(data["total_estimated_cost_inr"], (int, float))


def test_demo_valuation_returns_inr():
    client = get_client()
    response = client.post(
        "/api/valuation/property",
        json={
            "city": "Pune",
            "locality": "Kothrud",
            "property_type": "residential",
            "area_value": 1000,
            "area_unit": "sqft",
            "condition": "good",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["meta"]["mode"] == "demo"
    data = body["data"]
    assert data["indicative_value_mid_inr"] >= 0
    assert data["estimated_price_per_sqft_inr"] >= 0
