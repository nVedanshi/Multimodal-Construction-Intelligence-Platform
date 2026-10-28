"""Tests for image upload validation and edge cases."""

from __future__ import annotations

import io

from tests.conftest import get_client


def _make_upload_file(name: str, content: bytes, content_type: str):
    return (name, io.BytesIO(content), content_type)


def test_safety_rejects_invalid_file_type():
    client = get_client()
    files = {"site_photo": _make_upload_file("test.txt", b"not an image", "text/plain")}
    data = {"observation_log": "test observation"}
    response = client.post("/api/safety/analyze", data=data, files=files)
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"] == "invalid_upload"


def test_safety_accepts_valid_image_type():
    client = get_client()
    # Minimal valid PNG bytes (1x1 transparent)
    png_bytes = bytes(
        [
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00,
            0x0D, 0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
            0x00, 0x01, 0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89,
            0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63,
            0x00, 0x01, 0x00, 0x00, 0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4,
            0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0x82, 0x60, 0x68,
        ]
    )
    files = {"site_photo": _make_upload_file("test.png", png_bytes, "image/png")}
    data = {"observation_log": "test observation"}
    response = client.post("/api/safety/analyze", data=data, files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["meta"]["mode"] == "demo"


def test_crack_rejects_invalid_file_type():
    client = get_client()
    files = {"image": _make_upload_file("test.doc", b"not an image", "application/msword")}
    response = client.post("/api/crack/analyze", files=files)
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"] == "invalid_upload"


def test_crack_accepts_valid_image_type():
    client = get_client()
    png_bytes = bytes(
        [
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00,
            0x0D, 0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
            0x00, 0x01, 0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89,
            0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63,
            0x00, 0x01, 0x00, 0x00, 0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4,
            0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0x82, 0x60, 0x68,
        ]
    )
    files = {"image": _make_upload_file("crack.png", png_bytes, "image/png")}
    data = {"surface_type": "wall", "element_type": "load-bearing"}
    response = client.post("/api/crack/analyze", data=data, files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["meta"]["mode"] == "demo"
    data_body = body["data"]
    assert "crack_classification" in data_body
    assert "preliminary_severity" in data_body
    assert "disclaimer" in data_body
    assert "structural engineer" in data_body["disclaimer"].lower()


def test_valuation_negative_area_rejected():
    client = get_client()
    response = client.post(
        "/api/valuation/property",
        json={
            "city": "Pune",
            "locality": "Kothrud",
            "property_type": "residential",
            "area_value": -100,
            "area_unit": "sqft",
            "condition": "good",
        },
    )
    assert response.status_code in (400, 422)
    assert response.json()["success"] is False


def test_planning_invalid_quality():
    client = get_client()
    response = client.post(
        "/api/planning/project",
        json={
            "project_name": "Test",
            "construction_type": "residential",
            "intended_use": "house",
            "num_floors": 2,
            "quality_level": "invalid_quality",
        },
    )
    assert response.status_code in (400, 422)
    assert response.json()["success"] is False
