# pylint: disable=too-few-public-methods
"""Tests for the database helper module."""

from app import db as db_module


class FakeInsertResult:
    """Small fake insert result."""

    def __init__(self, inserted_id):
        """Store inserted id."""
        self.inserted_id = inserted_id


class FakeCollection:
    """Small fake Mongo collection for unit tests."""

    def __init__(self):
        """Initialize fake state."""
        self.inserted_doc = None
        self.updated_calls = []

    def insert_one(self, document):
        """Fake insert_one."""
        self.inserted_doc = document
        return FakeInsertResult("scan-123")

    def update_one(self, query, update):
        """Fake update_one."""
        self.updated_calls.append((query, update))

    def find_one_and_update(self, _query, _update, return_document=None):
        """Fake find_one_and_update."""
        return {
            "_id": "scan-123",
            "status": "processing",
            "return_document": return_document,
        }


def test_create_pending_scan_includes_new_fields(monkeypatch):
    """Pending scan creation should include actor and target emotion."""
    fake_collection = FakeCollection()
    monkeypatch.setattr(db_module, "scans", fake_collection)

    inserted_id = db_module.create_pending_scan("uploads/test.jpg", "happy", "Jerry")

    assert inserted_id == "scan-123"
    assert fake_collection.inserted_doc["actor_name"] == "Jerry"
    assert fake_collection.inserted_doc["image_path"] == "uploads/test.jpg"
    assert fake_collection.inserted_doc["target_emotion"] == "happy"
    assert fake_collection.inserted_doc["status"] == "pending"


def test_mark_scan_done_stores_grading_fields(monkeypatch):
    """Completed scan should store actor-grading results."""
    fake_collection = FakeCollection()
    monkeypatch.setattr(db_module, "scans", fake_collection)

    db_module.mark_scan_done(
        "scan-123",
        {
            "predicted_emotion": "happy",
            "emotion_scores": {"happy": 88.0},
            "match_score": 88.0,
            "passed": True,
            "face_detected": True,
            "processing_time_ms": 25,
        },
    )

    query, update = fake_collection.updated_calls[0]
    saved = update["$set"]

    assert query == {"_id": "scan-123"}
    assert saved["status"] == "done"
    assert saved["predicted_emotion"] == "happy"
    assert saved["match_score"] == 88.0
    assert saved["passed"] is True
    assert saved["face_detected"] is True
    assert saved["processing_time_ms"] == 25
    assert saved["error_message"] is None


def test_mark_scan_error_stores_error_fields(monkeypatch):
    """Failed scan should store the error message."""
    fake_collection = FakeCollection()
    monkeypatch.setattr(db_module, "scans", fake_collection)

    db_module.mark_scan_error("scan-123", "Image not found")

    query, update = fake_collection.updated_calls[0]
    saved = update["$set"]

    assert query == {"_id": "scan-123"}
    assert saved["status"] == "error"
    assert saved["match_score"] == 0.0
    assert saved["passed"] is False
    assert saved["face_detected"] is False
    assert saved["error_message"] == "Image not found"
