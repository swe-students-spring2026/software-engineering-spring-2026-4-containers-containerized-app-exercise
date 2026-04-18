"""Module for emotion detection using FER and capturing data autonomously."""

import os
import time
import datetime
from fer.fer import FER  # pylint: disable=import-error
import cv2  # pylint: disable=import-error
from db import get_collection, save_snapshot, SESSIONS_COLLECTION


def get_face_emotion():
    """Gets face emotion."""
    detector = FER(mtcnn=False)

    cap = cv2.VideoCapture(0)  # pylint: disable=no-member

    img_data = None

    if cap.isOpened():
        time.sleep(3)
        ret, frame = cap.read()
        cap.release()

        if ret:
            img_data = frame
    else:
        # when there is an error, use a fallback image
        fallback_path = os.path.join(os.getcwd(), "img.png")
        if os.path.exists(fallback_path):
            img_data = cv2.imread(fallback_path)  # pylint: disable=no-member

    if img_data is not None:
        detector.detect_emotions(img_data)
        result = detector.top_emotion(img_data)
        return img_data, result
    return None, None


def distraction_classification(data):
    """Classifies distraction based on emotion data."""
    if data is None:
        return "absent"
    emotion, score = data
    if emotion in ["happy", "neutral", "angry"]:
        return "focused"
    elif emotion in ["sad", "fear", "disgust", "surprise"]:
        return "distracted"
    else:
        return "unknown"


def store_data(img_frame, emotion, score, classification):
    """
    Fetches the active session and stores the snapshot data in MongoDB.
    """
    # 1. Find the active session
    sessions_col = get_collection(SESSIONS_COLLECTION)
    active_session = sessions_col.find_one({"is_active": True})

    if not active_session:
        print("No active focus session found. Skipping storage.")
        return

    # 2. Encode image to JPG binary
    success, buffer = cv2.imencode(".jpg", img_frame)
    if not success:
        print("Failed to encode image. Skipping storage.")
        return
    image_bytes = buffer.tobytes()

    # 3. Create snapshot document
    snapshot = {
        "user_id": active_session.get("user_id"),
        "session_id": active_session.get("_id"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
        "emotion": emotion,
        "confidence": score,
        "classification": classification,
        "image": image_bytes
    }

    # 4. Save to DB
    save_snapshot(snapshot)
    print(f"Snapshot stored successfully for session {active_session['_id']}")


if __name__ == "__main__":
    print("FocusFrame ML Client starting...")
    while True:
        frame, emotion_data = get_face_emotion()
        if emotion_data:
            emo, conf = emotion_data
            cl = distraction_classification(emotion_data)
            print(f"Detected {emo} ({conf:.2f}) -> {cl}")
            store_data(frame, emo, conf, cl)
        else:
            print("No face detected or capture failed.")

        # Capture frequency (can be updated from .env later)
        time.sleep(10)