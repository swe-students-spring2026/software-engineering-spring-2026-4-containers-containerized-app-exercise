from datetime import datetime, timezone
from pathlib import Path
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["emotion_db"]
scans = db["scans"]

image_path = (Path("sample_data") / "test.jpg").resolve().as_posix()

doc = {
    "image_path": image_path,
    "status": "pending",
    "created_at": datetime.now(timezone.utc),
    "started_at": None,
    "processed_at": None,
    "dominant_emotion": None,
    "emotion_scores": None,
    "face_detected": None,
    "processing_time_ms": None,
    "error_message": None,
}

result = scans.insert_one(doc)
print("Inserted document ID:", result.inserted_id)
print("Image path:", image_path)