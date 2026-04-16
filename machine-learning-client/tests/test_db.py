"""Tests for app.db."""
import pytest
from app import db


def test_save_practice_session_calls_insert_one(monkeypatch):
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
        inserted_id = "fake123"

    class FakeCollection:
        def insert_one(self, inserted_session):
            assert inserted_session == session
            return FakeInsertResult()

    # 🔥 THIS IS THE KEY LINE
    monkeypatch.setattr(db, "get_collection", lambda: FakeCollection())

    inserted_id = db.save_practice_session(session)

    assert inserted_id == "fake123"


def test_save_practice_session_invalid_input():
    with pytest.raises(ValueError):
        db.save_practice_session("not a dictionary")