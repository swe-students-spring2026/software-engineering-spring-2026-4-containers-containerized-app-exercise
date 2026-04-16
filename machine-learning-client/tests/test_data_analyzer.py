"""Tests for app.data_analyzer."""

import pytest

from app.data_analyzer import (
    count_words,
    count_filler_words,
    analyze_transcript,
)


def test_count_words_basic():
    """Test counting words in a basic transcript."""
    transcript = "Hello everyone! Um... How was your day?"
    assert count_words(transcript) == 7


def test_count_words_with_punctuation():
    """Test counting words when punctuation is present."""
    transcript = "Hello, everyone! I'm ready."
    assert count_words(transcript) == 4


def test_count_words_invalid_type():
    """Test count_words raises ValueError for invalid input type."""
    with pytest.raises(ValueError):
        count_words(123)


def test_count_filler_words_basic():
    """Test counting filler words in a transcript."""
    transcript = "Um I think like this is good, you know?"
    result = count_filler_words(transcript)

    assert result["um"] == 1
    assert result["uh"] == 0
    assert result["like"] == 1
    assert result["you know"] == 1
    assert result["literally"] == 0
    assert result["actually"] == 0
    assert result["basically"] == 0
    assert result["i mean"] == 0


def test_count_filler_words_case_insensitive():
    """Test filler word counting is case-insensitive."""
    transcript = "UM uh Like You Know"
    result = count_filler_words(transcript)

    assert result["um"] == 1
    assert result["uh"] == 1
    assert result["like"] == 1
    assert result["you know"] == 1


def test_count_filler_words_invalid_type():
    """Test count_filler_words raises ValueError for invalid input."""
    with pytest.raises(ValueError):
        count_filler_words(None)


def test_analyze_transcript_basic():
    """Test transcript analysis with one filler word and slow pace."""
    transcript = "Hello everyone um today"
    result = analyze_transcript(transcript, 30)

    assert result["word_count"] == 4
    assert result["filler_words"]["um"] == 1
    assert result["total_filler_count"] == 1
    assert result["wpm"] == 8
    assert result["pace_feedback"] == "slowwww..."
    assert result["filler_feedback"] == (
        "Good fluency. " "Only a few filler words were used."
    )


def test_analyze_transcript_no_filler_words():
    """Test transcript analysis when no filler words are present."""
    transcript = "Hello everyone today I am ready"
    result = analyze_transcript(transcript, 30)

    assert result["word_count"] == 6
    assert result["total_filler_count"] == 0
    assert result["filler_feedback"] == "Very fluent. No filler words detected."


def test_analyze_transcript_moderate_filler_words():
    """Test transcript analysis with moderate filler word usage."""
    transcript = "Um like actually I mean this is basically fine, you know?"
    result = analyze_transcript(transcript, 60)

    assert result["total_filler_count"] == 6
    assert result["filler_feedback"] == (
        "Moderate filler word usage. " "Try to pause instead of using filler words."
    )


def test_analyze_transcript_high_filler_words():
    """Test transcript analysis with high filler word usage."""
    transcript = "um um uh like like you know actually basically i mean um"
    result = analyze_transcript(transcript, 60)

    assert result["total_filler_count"] == 10
    assert result["filler_feedback"] == (
        "Moderate filler word usage. " "Try to pause instead of using filler words."
    )


def test_analyze_transcript_good_pace():
    """Test transcript analysis when pace is in the ideal range."""
    transcript = "one two three four five six seven eight nine ten"
    result = analyze_transcript(transcript, 5)

    assert result["wpm"] == 120
    assert result["pace_feedback"] == "perfect :)"


def test_analyze_transcript_too_fast():
    """Test transcript analysis when speaking pace is too fast."""
    transcript = "one two three four five six seven eight nine ten"
    result = analyze_transcript(transcript, 3)

    assert result["wpm"] == 200
    assert result["pace_feedback"] == "so fast!!!!!"


def test_analyze_transcript_empty_transcript():
    """Test analyze_transcript raises ValueError for empty transcript."""
    with pytest.raises(ValueError):
        analyze_transcript("", 30)


def test_analyze_transcript_whitespace_transcript():
    """Test analyze_transcript raises ValueError for whitespace transcript."""
    with pytest.raises(ValueError):
        analyze_transcript("   ", 30)


def test_analyze_transcript_invalid_duration_zero():
    """Test analyze_transcript raises ValueError for zero duration."""
    with pytest.raises(ValueError):
        analyze_transcript("Hello world", 0)


def test_analyze_transcript_invalid_duration_negative():
    """Test analyze_transcript raises ValueError for negative duration."""
    with pytest.raises(ValueError):
        analyze_transcript("Hello world", -5)


def test_analyze_transcript_invalid_duration_type():
    """Test analyze_transcript raises ValueError for invalid duration type."""
    with pytest.raises(ValueError):
        analyze_transcript("Hello world", "30")
