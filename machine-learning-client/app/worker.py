"""Background worker that processes pending scan jobs."""

import os
import time

from app.config import POLL_INTERVAL
from app.db import get_next_pending_scan, mark_scan_done, mark_scan_error
from app.emotion_service import analyze_image


def run_worker():
    """Continuously poll MongoDB and process pending scan jobs."""
    print("ML worker started")

    while True:
        scan = get_next_pending_scan()

        if not scan:
            time.sleep(POLL_INTERVAL)
            continue

        try:
            image_path = scan["image_path"]

            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")

            result = analyze_image(image_path)
            mark_scan_done(scan["_id"], result)
            print(f"Processed scan {scan['_id']}")

        except Exception as exc:  # pylint: disable=broad-exception-caught
            mark_scan_error(scan["_id"], str(exc))
            print(f"Error processing scan {scan['_id']}: {exc}")


if __name__ == "__main__":
    run_worker()
