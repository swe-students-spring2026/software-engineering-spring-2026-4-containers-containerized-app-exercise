import time
from deepface import DeepFace


def analyze_image(image_path):
    start = time.time()

    result = DeepFace.analyze(
        img_path=image_path,
        actions=["emotion"],
        enforce_detection=False
    )

    if isinstance(result, list):
        result = result[0]

    emotions = result["emotion"]
    dominant_emotion = result["dominant_emotion"]
    processing_time_ms = int((time.time() - start) * 1000)

    return {
        "dominant_emotion": dominant_emotion,
        "emotion_scores": {
            "angry": round(float(emotions.get("angry", 0)), 2),
            "disgust": round(float(emotions.get("disgust", 0)), 2),
            "fear": round(float(emotions.get("fear", 0)), 2),
            "happy": round(float(emotions.get("happy", 0)), 2),
            "sad": round(float(emotions.get("sad", 0)), 2),
            "surprise": round(float(emotions.get("surprise", 0)), 2),
            "neutral": round(float(emotions.get("neutral", 0)), 2),
        },
        "face_detected": True,
        "processing_time_ms": processing_time_ms,
    }