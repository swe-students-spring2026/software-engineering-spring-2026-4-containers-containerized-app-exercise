"""Helpers for saving realtime predictions to MongoDB."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ROOT_ENV)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sign_language_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "predictions")

CLIENT = MongoClient(MONGO_URI)
DB = CLIENT[MONGO_DB_NAME]
COLLECTION = DB[MONGO_COLLECTION]


def log_prediction(
    predicted_label: str,
    confidence: float,
    current_text: str = "",
    source: str = "browser_camera",
    frame_number: int | None = None,
) -> None:
    """Insert one prediction record into MongoDB."""
    document = {
        "timestamp": datetime.now(timezone.utc),
        "predicted_label": predicted_label,
        "confidence": float(confidence),
        "current_text": current_text,
        "source": source,
        "frame_number": frame_number,
    }
    COLLECTION.insert_one(document)
