from __future__ import annotations

from app.config import get_settings
from app.database import get_db

settings = get_settings()


def get_settings_dependency():
    return settings


def get_db_dependency():
    return get_db
