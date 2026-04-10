"""Tests for app.db."""

from app.db import save_practice_session


def test_save_practice_session():
    """Test that a practice session can be saved."""
    inserted_id = save_practice_session(
        filename  = "demo.wav",
        transcript = "Hello everyone um today I want to introduce myself",
        analysis  = {
            "word_count"        : 8,
            "wpm"               : 120.5,
            "filler_words"      : {"um": 1, "uh": 0, "like": 0},
            "total_filler_count": 1,
        },
    )

    assert inserted_id is not None
    