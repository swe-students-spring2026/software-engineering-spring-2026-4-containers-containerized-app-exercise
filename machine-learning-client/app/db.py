"""MongoDB helper functions for scan processing."""

from datetime import datetime, timezone

from pymongo import MongoClient, ReturnDocument

from app.config import COLLECTION_NAME, DB_NAME, MONGO_URI

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
scans = db[COLLECTION_NAME]


def utc_now():
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


def get_next_pending_scan():
    """Find one pending scan and mark it as processing."""
    return scans.find_one_and_update(
        {"status": "pending"},
        {"$set": {"status": "processing", "started_at": utc_now()}},
        return_document=ReturnDocument.AFTER,
    )


def mark_scan_done(scan_id, result):
    """Mark a scan as completed and store analysis results."""
    scans.update_one(
        {"_id": scan_id},
        {
            "$set": {
                "status": "done",
                "processed_at": utc_now(),
                "dominant_emotion": result["dominant_emotion"],
                "emotion_scores": result["emotion_scores"],
                "face_detected": result["face_detected"],
                "processing_time_ms": result["processing_time_ms"],
                "error_message": None,
            }
        },
    )


def mark_scan_error(scan_id, message):
    """Mark a scan as failed and store the error message."""
    scans.update_one(
        {"_id": scan_id},
        {
            "$set": {
                "status": "error",
                "processed_at": utc_now(),
                "error_message": message,
            }
        },
    )
