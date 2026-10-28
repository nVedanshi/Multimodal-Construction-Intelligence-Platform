"""Tests for daily site task persistence endpoints."""

from __future__ import annotations

from tests.conftest import get_client


def _create_plan(client, date: str = "2026-10-29"):
    return client.post(
        "/api/daily-site/plan",
        json={
            "date": date,
            "project_phase": "foundation",
            "planned_activities": "excavation",
            "workforce_availability": "4 workers",
            "materials": "cement",
            "equipment": "excavator",
            "site_conditions": "dry",
            "constraints": "none",
        },
    )


def test_daily_plan_persists_tasks():
    client = get_client()
    response = _create_plan(client, "2026-10-29")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["meta"]["mode"] == "demo"
    tasks = body["data"]["prioritized_tasks"]
    assert len(tasks) >= 1
    task_id = tasks[0]["id"]

    # Fetch persisted tasks
    get_response = client.get(
        "/api/daily-site/tasks", params={"plan_date": "2026-10-29"}
    )
    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["success"] is True
    persisted = get_body["data"]
    assert any(t["task_id"] == task_id for t in persisted)
    assert any(t["completed"] is False for t in persisted if t["task_id"] == task_id)


def test_daily_task_completion_toggle():
    client = get_client()
    _create_plan(client, "2026-10-30")
    tasks_response = client.get(
        "/api/daily-site/tasks", params={"plan_date": "2026-10-30"}
    )
    tasks = tasks_response.json()["data"]
    task_id = tasks[0]["task_id"]

    # Mark completed
    patch_response = client.patch(
        f"/api/daily-site/tasks/{task_id}/complete",
        params={"plan_date": "2026-10-30"},
        json={"task_id": task_id, "completed": True},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["data"]["completed"] is True

    # Verify persisted
    get_response = client.get(
        "/api/daily-site/tasks", params={"plan_date": "2026-10-30"}
    )
    updated = get_response.json()["data"]
    assert any(t["task_id"] == task_id and t["completed"] is True for t in updated)

    # Mark incomplete again
    patch_response2 = client.patch(
        f"/api/daily-site/tasks/{task_id}/complete",
        params={"plan_date": "2026-10-30"},
        json={"task_id": task_id, "completed": False},
    )
    assert patch_response2.status_code == 200
    assert patch_response2.json()["data"]["completed"] is False


def test_daily_task_missing_date():
    client = get_client()
    response = client.patch(
        "/api/daily-site/tasks/demo-1/complete",
        json={"task_id": "demo-1", "completed": True},
    )
    assert response.status_code == 400
    assert response.json()["success"] is False


def test_daily_task_not_found():
    client = get_client()
    response = client.patch(
        "/api/daily-site/tasks/nonexistent-id/complete",
        params={"plan_date": "2026-10-31"},
        json={"task_id": "nonexistent-id", "completed": True},
    )
    assert response.status_code == 404
    assert response.json()["success"] is False


def test_daily_plan_missing_date_field():
    client = get_client()
    response = client.post("/api/daily-site/plan", json={})
    assert response.status_code in (400, 422)
    body = response.json()
    assert body["success"] is False
