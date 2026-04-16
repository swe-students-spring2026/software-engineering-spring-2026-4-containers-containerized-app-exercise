"""Tests for app.db."""

# pylint: disable=too-few-public-methods,import-error

import pytest
from app import db


def test_save_practice_session_calls_insert_one(monkeypatch):
    """Test that a practice session is inserted and its ID is returned."""
    session = {
        "audio_file": "record_outputs/demo.wav",
        "duration_seconds": 6,
        "transcript": "Hello everyone um today I want to introduce myself",
        "analysis": {
            "word_count": 8,
            "wpm": 80,
        },
    }

    class FakeInsertResult:
        """Fake insert result."""

        inserted_id = "fake123"

    class FakeCollection:
        """Fake Mongo collection."""

        def insert_one(self, inserted_session):
            """Mock insert_one."""
            assert inserted_session == session
            return FakeInsertResult()

    def fake_get_collection():
        """Return fake collection."""
        return FakeCollection()

    monkeypatch.setattr(db, "get_collection", fake_get_collection)

    inserted_id = db.save_practice_session(session)

    assert inserted_id == "fake123"


def test_save_practice_session_invalid_input():
    """Test invalid input raises ValueError."""
    with pytest.raises(ValueError):
        db.save_practice_session("not a dictionary")
