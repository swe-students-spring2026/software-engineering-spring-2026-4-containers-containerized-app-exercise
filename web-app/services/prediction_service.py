"""Service functions for retrieving and formatting prediction data."""

from collections import Counter
from statistics import mean
from typing import Any

from db.mongo import get_predictions_collection


def _serialize_prediction(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convert a MongoDB prediction document into a JSON-friendly dict."""
    if not doc:
        return None

    timestamp = doc.get("timestamp")
    if hasattr(timestamp, "isoformat"):
        timestamp = timestamp.isoformat()

    return {
        "id": str(doc.get("_id", "")),
        "timestamp": timestamp,
        "predicted_label": doc.get("predicted_label", "N/A"),
        "confidence": round(float(doc.get("confidence", 0.0)), 3),
        "current_text": doc.get("current_text", ""),
        "source": doc.get("source", ""),
        "frame_number": doc.get("frame_number"),
    }


def get_latest_prediction():
    """Return the most recent prediction document."""
    collection = get_predictions_collection()
    doc = collection.find_one(sort=[("_id", -1)])
    return _serialize_prediction(doc)


def get_recent_predictions(
    limit: int = 10,
    search_query: str = "",
    sort_order: str = "desc",
):
    """Return recent prediction documents, optionally filtered by label."""
    collection = get_predictions_collection()

    query = {}
    if search_query:
        query = {
            "predicted_label": {
                "$regex": search_query,
                "$options": "i",
            }
        }

    sort_direction = 1 if sort_order == "asc" else -1
    docs = collection.find(query).sort("_id", sort_direction).limit(limit)
    return [_serialize_prediction(doc) for doc in docs]


def get_prediction_stats(limit: int = 100):
    """Return aggregate statistics computed from recent predictions."""
    recent = get_recent_predictions(limit)

    if not recent:
        return {
            "total_predictions": 0,
            "average_confidence": 0.0,
            "top_label": "N/A",
            "label_counts": {},
        }

    labels = [item["predicted_label"] for item in recent if item["predicted_label"]]
    confidences = [item["confidence"] for item in recent]

    label_counts = dict(Counter(labels))
    top_label = max(label_counts, key=label_counts.get) if label_counts else "N/A"

    return {
        "total_predictions": len(recent),
        "average_confidence": round(mean(confidences), 3),
        "top_label": top_label,
        "label_counts": label_counts,
    }
