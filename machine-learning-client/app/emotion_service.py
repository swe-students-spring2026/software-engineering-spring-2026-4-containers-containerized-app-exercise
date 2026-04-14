"""Emotion analysis service for image scans."""

import time


def analyze_image(image_path):
    """Return a simple placeholder emotion-analysis result."""
    if not image_path:
        raise ValueError("image_path is required")

    start = time.time()

    emotions = {
        "angry": 2.58,
        "disgust": 1.53,
        "fear": 2.15,
        "happy": 44.75,
        "sad": 2.0,
        "surprise": 2.32,
        "neutral": 15.67,
    }

    dominant_emotion = max(emotions, key=emotions.get)
    processing_time_ms = int((time.time() - start) * 1000)

    return {
        "dominant_emotion": dominant_emotion,
        "emotion_scores": emotions,
        "face_detected": True,
        "processing_time_ms": processing_time_ms,
    }
