"""Emotion analysis service for actor-expression grading."""

import time

from deepface import DeepFace

from app.config import PASS_THRESHOLD
from app.models import ALLOWED_EMOTIONS


def _normalize_emotion_scores(raw_scores):
    """Return all supported emotions with float values."""
    normalized = {}
    for emotion in ALLOWED_EMOTIONS:
        normalized[emotion] = float(raw_scores.get(emotion, 0.0))
    return normalized


def analyze_image(image_path, target_emotion):
    """Analyze an image and score how well it matches the target emotion."""
    if not image_path:
        raise ValueError("image_path is required")
    if not target_emotion:
        raise ValueError("target_emotion is required")

    target_emotion = target_emotion.lower()
    if target_emotion not in ALLOWED_EMOTIONS:
        raise ValueError(f"Unsupported target_emotion: {target_emotion}")

    start = time.time()

    analysis = DeepFace.analyze(
        img_path=image_path,
        actions=["emotion"],
        enforce_detection=False,
        detector_backend="opencv",
    )

    if isinstance(analysis, list):
        analysis = analysis[0]

    raw_scores = analysis.get("emotion")
    if not raw_scores:
        raise ValueError("Model did not return emotion scores")

    emotion_scores = _normalize_emotion_scores(raw_scores)
    predicted_emotion = max(emotion_scores, key=emotion_scores.get)
    match_score = emotion_scores[target_emotion]

    region = analysis.get("region") or {}
    face_detected = bool(region) or analysis.get("face_confidence", 0) > 0

    processing_time_ms = int((time.time() - start) * 1000)
    passed = match_score >= PASS_THRESHOLD

    return {
        "predicted_emotion": predicted_emotion,
        "emotion_scores": emotion_scores,
        "match_score": match_score,
        "passed": passed,
        "face_detected": face_detected,
        "processing_time_ms": processing_time_ms,
    }
