"""Tests for the emotion service module."""

from app.emotion_service import analyze_image


def test_analyze_image_returns_expected_keys():
    """analyze_image should return all required output fields."""
    result = analyze_image("sample_data/test.jpg")

    assert "dominant_emotion" in result
    assert "emotion_scores" in result
    assert "face_detected" in result
    assert "processing_time_ms" in result
    assert result["face_detected"] is True
    assert isinstance(result["emotion_scores"], dict)
