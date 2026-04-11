from app.emotion_service import analyze_image

def test_analyze_image_returns_expected_keys(monkeypatch):
    def fake_analyze(*args, **kwargs):
        return {
            "dominant_emotion": "happy",
            "emotion_scores": {
                "angry": 1,
                "disgust": 0,
                "fear": 2,
                "happy": 80,
                "sad": 4,
                "surprise": 3,
                "neutral": 10,
            },
            "face_detected": True,
            "processing_time_ms": 100,
        }