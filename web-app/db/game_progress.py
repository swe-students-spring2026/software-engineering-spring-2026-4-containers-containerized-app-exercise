"""MongoDB helpers for persisting game progress."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from flask import current_app

from db.mongo import get_db

DEFAULT_SESSION_ID = "default_user"


def get_game_progress_collection():
    """Return the configured MongoDB collection for game progress."""
    database = get_db()
    return database[current_app.config["GAME_PROGRESS_COLLECTION"]]


def get_progress(session_id: str = DEFAULT_SESSION_ID) -> dict[str, Any] | None:
    """Fetch saved progress for the given session id."""
    collection = get_game_progress_collection()
    return collection.find_one({"session_id": session_id}, {"_id": 0})


def save_progress(
    progress: dict[str, Any], session_id: str = DEFAULT_SESSION_ID
) -> None:
    """Upsert saved progress for the given session id."""
    collection = get_game_progress_collection()
    payload = dict(progress)
    payload["session_id"] = session_id
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()

    collection.update_one(
        {"session_id": session_id},
        {"$set": payload},
        upsert=True,
    )
