from __future__ import annotations

import os

os.environ["DATABASE_URL"] = "sqlite:///./test_construction.db"
os.environ["DEMO_MODE"] = "true"

from fastapi.testclient import TestClient  # noqa: E402
from app.database import init_db  # noqa: E402
from app.main import app  # noqa: E402

# Initialize database tables before creating the test client.
init_db()

client = TestClient(app)


def get_client():
    return client
