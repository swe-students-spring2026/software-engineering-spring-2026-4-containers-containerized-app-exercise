"""Tests for the emotion service module."""

import pytest

from app import emotion_service


def test_analyze_image_returns_expected_keys(monkeypatch):
    """analyze_image should return all required output fields."""

    def fake_analyze(**_kwargs):
        return [
            {
                "emotion": {
                    "angry": 1.0,
                    "disgust": 0.5,
                    "fear": 2.0,
                    "happy": 91.0,
                    "sad": 1.5,
                    "surprise": 3.0,
                    "neutral": 1.0,
                },
                "region": {"x": 1, "y": 2, "w": 3, "h": 4},
            }
        ]

    monkeypatch.setattr(emotion_service.DeepFace, "analyze", fake_analyze)

    result = emotion_service.analyze_image("sample_data/test.jpg", "happy")

    assert result["predicted_emotion"] == "happy"
    assert result["match_score"] == 91.0
    assert result["passed"] is True
    assert result["face_detected"] is True
    assert isinstance(result["emotion_scores"], dict)
    assert "processing_time_ms" in result


def test_analyze_image_rejects_missing_target():
    """analyze_image should reject a missing target emotion."""
    with pytest.raises(ValueError, match="target_emotion is required"):
        emotion_service.analyze_image("sample_data/test.jpg", "")


def test_analyze_image_rejects_unsupported_target():
    """analyze_image should reject unsupported emotions."""
    with pytest.raises(ValueError, match="Unsupported target_emotion"):
        emotion_service.analyze_image("sample_data/test.jpg", "confused")


def test_analyze_image_raises_when_model_returns_no_scores(monkeypatch):
    """analyze_image should fail if the model gives no emotion scores."""

    def fake_analyze(**_kwargs):
        return {"emotion": None}

    monkeypatch.setattr(emotion_service.DeepFace, "analyze", fake_analyze)

    with pytest.raises(ValueError, match="Model did not return emotion scores"):
        emotion_service.analyze_image("sample_data/test.jpg", "happy")
