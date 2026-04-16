"""Tests for app.db."""

from app.db import save_practice_session


def test_save_practice_session():
    """Test that a practice session can be saved."""
    session = {
        "audio_file": "record_outputs/demo.wav",
        "duration_seconds": 6,
        "transcript": ("Hello everyone um today I want to introduce myself"),
        "analysis": {
            "word_count": 8,
            "wpm": 80,
            "filler_words": {
                "um": 1,
                "uh": 0,
                "like": 0,
                "you know": 0,
                "literally": 0,
                "actually": 0,
                "basically": 0,
                "i mean": 0,
            },
            "total_filler_count": 1,
            "pace_feedback": "slowwww...",
            "filler_feedback": ("Good fluency. Only a few filler words were used."),
        },
    }

    inserted_id = save_practice_session(session)

    assert inserted_id is not None
