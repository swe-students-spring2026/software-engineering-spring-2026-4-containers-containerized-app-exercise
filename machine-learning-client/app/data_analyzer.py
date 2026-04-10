"""Utilities for analyzing speech transcripts."""

import re

FILLER_WORDS = [
    "um",
    "uh",
    "like",
    "you know",
    "literally",
    "actually",
    "basically",
    "i mean",
]


def count_words(transcript: str) -> int:
    """
    Count the total number of words in a transcript.

    Args:
        transcript: Input transcript string.

    Returns:
        Total number of words.
    """
    if not isinstance(transcript, str):
        raise ValueError("transcript must be string")

    words = re.findall(r"\b[\w']+\b", transcript.lower())
    return len(words)


def count_filler_words(transcript: str) -> dict:
    """
    Count occurrences of predefined filler words/phrases.

    Args:
        transcript: Input transcript string.

    Returns:
        A dictionary mapping each filler word to its count.
    """
    if not isinstance(transcript, str):
        raise ValueError("transcript must be a string")

    text = transcript.lower()
    counts = {}

    for w in FILLER_WORDS:
        # find words if in the FILLER_WORDS
        pattern = r"\b" + re.escape(w) + r"\b"
        matches = re.findall(pattern, text)
        counts[w] = len(matches)

    return counts


def analyze_transcript(transcript: str, duration_seconds: float) -> dict:
    """
    Analyze a transcript for total words, filler word usage, and WPM.

    Args:
        transcript: Input transcript string.
        duration_seconds: Audio duration in seconds.

    Returns:
        A dictionary containing analysis results.
    """
    if not isinstance(transcript, str) or not transcript.strip():
        raise ValueError("transcript must be a non-empty string")

    if not isinstance(duration_seconds, (int, float)) or duration_seconds <= 0:
        raise ValueError("duration_seconds must be a positive number")

    word_count = count_words(transcript)
    filler_words = count_filler_words(transcript)
    total_filler_count = sum(filler_words.values())
    wpm = round((word_count / duration_seconds) * 60)

    # pace feedback
    if wpm < 100:
        pace_feedback = "slowwww..."
    elif wpm <= 160:
        pace_feedback = "perfect :)"
    else:
        pace_feedback = "so fast!!!!!"

    # filler feedback
    if total_filler_count == 0:
        filler_feedback = "Very fluent. No filler words detected."
    elif total_filler_count <= 5:
        filler_feedback = "Good fluency. Only a few filler words were used."
    elif total_filler_count <= 10:
        filler_feedback = (
            "Moderate filler word usage. "
            + "Try to pause instead of using filler words."
        )
    else:
        filler_feedback = (
            "High filler word usage. "
            "Practice slowing down and organizing thoughts before speaking."
        )

    return {
        "word_count": word_count,
        "filler_words": filler_words,
        "total_filler_count": total_filler_count,
        "wpm": wpm,
        "pace_feedback": pace_feedback,
        "filler_feedback": filler_feedback,
    }
