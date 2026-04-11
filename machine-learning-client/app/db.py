from datetime import datetime, timezone
from pymongo import MongoClient, ReturnDocument
from app.config import MONGO_URI, DB_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
scans = db[COLLECTION_NAME]


def utc_now():
    return datetime.now(timezone.utc)


def get_next_pending_scan():
    return scans.find_one_and_update(
        {"status": "pending"},
        {"$set": {"status": "processing", "started_at": utc_now()}},
        return_document=ReturnDocument.AFTER,
    )


def mark_scan_done(scan_id, result):
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