"""Tests for database connection."""
from db import speeches_collection
# pylint: disable=import-error


def test_db_connection():
    """Test that database connection works."""
    result = speeches_collection.insert_one({"test": "connection"})
    assert result.inserted_id is not None
    speeches_collection.delete_one({"_id": result.inserted_id})


def test_insert_speech():
    """Test inserting a speech document into the database."""
    speech = {
        "user_id": "test_user_1",
        "title": "test speech",
        "timestamp": "2026-04-15T22:00:00",
        "transcript": "this is a test",
        "wpm": 120.0,
        "filler_count": 3,
        "filler_words_found": ["um", "like", "uh"],
        "volume_score": 80,
        "pitch_variety_score": 75,
        "pace_score": 85,
        "overall_score": 80,
    }

    result = speeches_collection.insert_one(speech)
    assert result.inserted_id is not None

    saved_speech = speeches_collection.find_one({"_id": result.inserted_id})
    assert saved_speech is not None
    assert saved_speech["title"] == "test speech"
    assert saved_speech["wpm"] == 120.0
    assert saved_speech["filler_count"] == 3

    speeches_collection.delete_one({"_id": result.inserted_id})
