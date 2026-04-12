"""
Machine learning client for garbage classification.
Captures image from camera, runs inference via Roboflow,
and saves results to MongoDB.
"""

import os
import logging
import time

# from datetime import datetime, timezone

import cv2
from dotenv import load_dotenv
from roboflow import Roboflow

from database import get_database, save_result

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# How often to capture + analyze (seconds)
CAPTURE_INTERVAL = int(os.environ.get("CAPTURE_INTERVAL", 30))


def capture_image(output_path="capture.jpg"):
    """
    Capture a single frame from the camera and save it.

    Args:
        output_path: file path to save the captured image

    Returns:
        output_path if successful, None if failed
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Could not open camera.")
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret:
        logger.error("Failed to capture frame.")
        return None

    cv2.imwrite(output_path, frame)
    logger.info("Image captured: %s", output_path)
    return output_path


def run_inference(image_path):
    """
    Send image to Roboflow and return predictions.

    Args:
        image_path: path to image file

    Returns:
        list of prediction dicts
    """
    rf = Roboflow(api_key=os.environ["ROBOFLOW_API_KEY"])
    project = rf.workspace("material-identification").project(
        "garbage-classification-3"
    )
    model = project.version(2).model

    result = model.predict(image_path, confidence=40, overlap=30)
    predictions = result.json().get("predictions", [])
    logger.info("Detected %d object(s).", len(predictions))
    return predictions


def process_once(collection, image_path="capture.jpg"):
    """
    Run one full cycle: capture → infer → save to DB.

    Args:
        collection: pymongo collection
        image_path: where to save the captured image

    Returns:
        inserted MongoDB document id, or None if failed
    """
    path = capture_image(image_path)
    if path is None:
        logger.warning("Skipping cycle — no image captured.")
        return None

    predictions = run_inference(path)
    doc_id = save_result(collection, path, predictions)
    logger.info("Saved to DB with id: %s", doc_id)
    return doc_id


def run_loop(collection):
    """
    Continuously capture and analyze on a schedule.

    Args:
        collection: pymongo collection
    """
    logger.info("Starting ML client loop every %d seconds.", CAPTURE_INTERVAL)
    while True:
        try:
            process_once(collection)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Error during cycle: %s", exc)
        time.sleep(CAPTURE_INTERVAL)


if __name__ == "__main__":
    db = get_database()
    col = db["detections"]
    run_loop(col)
    # path = capture_image("capture.jpg")
    # predictions = run_inference("capture.jpg")
    # print(predictions)
