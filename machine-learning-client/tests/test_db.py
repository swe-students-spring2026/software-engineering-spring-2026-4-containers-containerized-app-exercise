"""Tests for MongoDB helper functions."""

from datetime import timezone

from app import db as db_module


class FakeCollection:
    """Simple fake MongoDB collection for unit tests."""

    def __init__(self):
        self.find_one_and_update_args = None
        self.update_calls = []

    def find_one_and_update(self, query, update, return_document=None):
        """Store arguments and return a fake processing scan."""
        self.find_one_and_update_args = (query, update, return_document)
        return {"_id": "scan-1", "status": "processing"}

    def update_one(self, query, update):
        """Store update calls."""
        self.update_calls.append((query, update))


def test_utc_now_is_timezone_aware():
    """utc_now should return a timezone-aware datetime."""
    now = db_module.utc_now()
    assert now.tzinfo == timezone.utc


def test_get_next_pending_scan(monkeypatch):
    """Should claim one pending scan and mark it processing."""
    fake_collection = FakeCollection()
    monkeypatch.setattr(db_module, "scans", fake_collection)

    result = db_module.get_next_pending_scan()

    assert result["_id"] == "scan-1"
    query, update, _ = fake_collection.find_one_and_update_args
    assert query == {"status": "pending"}
    assert update["$set"]["status"] == "processing"
    assert "started_at" in update["$set"]


def test_mark_scan_done(monkeypatch):
    """Should store a completed scan result."""
    fake_collection = FakeCollection()
    monkeypatch.setattr(db_module, "scans", fake_collection)

    result = {
        "dominant_emotion": "happy",
        "emotion_scores": {"happy": 90.0},
        "face_detected": True,
        "processing_time_ms": 12,
    }

    db_module.mark_scan_done("scan-1", result)

    query, update = fake_collection.update_calls[0]
    assert query == {"_id": "scan-1"}
    assert update["$set"]["status"] == "done"
    assert update["$set"]["dominant_emotion"] == "happy"
    assert update["$set"]["face_detected"] is True
    assert update["$set"]["processing_time_ms"] == 12
    assert update["$set"]["error_message"] is None


def test_mark_scan_error(monkeypatch):
    """Should store an error message for a failed scan."""
    fake_collection = FakeCollection()
    monkeypatch.setattr(db_module, "scans", fake_collection)

    db_module.mark_scan_error("scan-1", "file missing")

    query, update = fake_collection.update_calls[0]
    assert query == {"_id": "scan-1"}
    assert update["$set"]["status"] == "error"
    assert update["$set"]["error_message"] == "file missing"
