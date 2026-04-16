"""Game challenge definitions and progress helpers."""

from __future__ import annotations

from typing import Any

CHALLENGES = [
    {"display_text": "CAT", "target_text": "CAT", "image": "cat.jpg"},
    {"display_text": "DOG", "target_text": "DOG", "image": "dog.jpg"},
    {"display_text": "BOOK", "target_text": "BOOK", "image": "book.jpg"},
    {"display_text": "APPLE", "target_text": "APPLE", "image": "apple.jpg"},
    {"display_text": "PHONE", "target_text": "PHONE", "image": "phone.jpg"},
    {"display_text": "MUSIC", "target_text": "MUSIC", "image": "music.jpg"},
    {
        "display_text": "I LOVE YOU",
        "target_text": "ILOVEYOU",
        "image": "i_love_you.jpg",
    },
    {
        "display_text": "THANK YOU",
        "target_text": "THANKYOU",
        "image": "thank_you.jpg",
    },
    {
        "display_text": "SMART HOME",
        "target_text": "SMARTHOME",
        "image": "smart_home.jpg",
    },
    {
        "display_text": "DATA SCIENCE",
        "target_text": "DATASCIENCE",
        "image": "data_science.jpg",
    },
]


def get_default_progress() -> dict[str, Any]:
    """Return the default game progress state."""
    return {
        "current_level": 0,
        "completed_words": [],
        "earned_medals": [],
        "game_status": "idle",
    }


def sanitize_progress(progress: dict[str, Any] | None) -> dict[str, Any]:
    """Return a safe progress payload with all expected keys present."""
    default = get_default_progress()
    if not progress:
        return default

    return {
        "current_level": int(progress.get("current_level", 0)),
        "completed_words": list(progress.get("completed_words", [])),
        "earned_medals": list(progress.get("earned_medals", [])),
        "game_status": str(progress.get("game_status", "idle")),
    }
