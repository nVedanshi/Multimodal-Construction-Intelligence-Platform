from __future__ import annotations

import os
import re
import uuid
from typing import Optional

from app.config import get_settings

settings = get_settings()


def sanitize_filename(original_filename: str) -> str:
    """Return a safe, unique filename derived from the original."""
    base = os.path.basename(original_filename or "upload")
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    if not base:
        base = "upload"
    unique = uuid.uuid4().hex[:8]
    name, ext = os.path.splitext(base)
    return "%s_%s%s" % (name[:64], unique, ext)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def validate_upload(filename: str, size_bytes: int) -> Optional[str]:
    """Validate an uploaded file. Returns an error message string or None."""
    if not filename:
        return "No filename provided."
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        return (
            "Unsupported file type '%s'. Allowed: %s."
            % (ext or "unknown", ", ".join(sorted(settings.ALLOWED_IMAGE_EXTENSIONS)))
        )
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        return (
            "File too large (%.1f MB). Maximum allowed is %d MB."
            % (size_bytes / (1024 * 1024), settings.MAX_UPLOAD_SIZE_MB)
        )
    return None


def save_upload(file_bytes: bytes, filename: str, subdir: str = "uploads") -> str:
    """Save uploaded bytes to disk and return the stored path."""
    base_dir = subdir or settings.UPLOAD_DIR
    ensure_dir(base_dir)
    safe_name = sanitize_filename(filename)
    dest = os.path.join(base_dir, safe_name)
    with open(dest, "wb") as f:
        f.write(file_bytes)
    return dest
