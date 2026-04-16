"""Background worker that processes pending acting-attempt jobs."""

import os
import time

from app.config import POLL_INTERVAL
from app.db import get_next_pending_scan, mark_scan_done, mark_scan_error
from app.emotion_service import analyze_image


def process_next_scan():
    """Process one pending scan if one exists."""
    scan = get_next_pending_scan()
    if not scan:
        return False

    try:
        image_path = scan.get("image_path")
        target_emotion = scan.get("target_emotion")

        if not image_path:
            raise ValueError("image_path is required")
        if not target_emotion:
            raise ValueError("target_emotion is required")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        result = analyze_image(image_path, target_emotion)
        mark_scan_done(scan["_id"], result)
        print(f"Processed scan {scan['_id']}")

    except Exception as exc:  # pylint: disable=broad-exception-caught
        mark_scan_error(scan["_id"], str(exc))
        print(f"Error processing scan {scan['_id']}: {exc}")

    return True


def run_worker():
    """Continuously poll MongoDB and process pending scan jobs."""
    print("ML worker started")

    while True:
        processed = process_next_scan()
        if not processed:
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_worker()
