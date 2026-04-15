"""Helpers for saving realtime predictions to MongoDB."""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sign_language_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "prediction_logs")

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB_NAME]
_collection = _db[MONGO_COLLECTION]


def log_prediction(
    predicted_label: str,
    confidence: float,
    current_text: str = "",
    source: str = "webcam",
    frame_number: int | None = None,
) -> None:
    """Insert one prediction record into MongoDB."""
    doc = {
        "timestamp": datetime.now(timezone.utc),
        "predicted_label": predicted_label,
        "confidence": float(confidence),
        "current_text": current_text,
        "source": source,
        "frame_number": frame_number,
    }
    _collection.insert_one(doc)