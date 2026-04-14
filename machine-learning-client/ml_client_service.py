import base64
import json
import threading
from argparse import Namespace
from datetime import datetime

import requests
from flask import Flask, request
from pymongo import MongoClient

from config import Config
from food_detection import DEFAULT_FOOD_CLASSES, run_detection

app = Flask(__name__)
db = MongoClient(Config.MONGO_URI)[Config.DB_NAME]


def _run(task_id, filename, image_bytes):
    task_dir = Config.RUNTIME_FOLDER / task_id
    input_dir = task_dir / "input"
    output_dir = task_dir / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / filename).write_bytes(image_bytes)

    try:
        run_detection(Namespace(
            input=str(input_dir),
            output=str(output_dir),
            classes=DEFAULT_FOOD_CLASSES,
            box_thresh=0.35,
            text_thresh=0.25,
            device="",
            save_crop=False,
        ))
        with open(output_dir / "detection_results.json", encoding="utf-8") as fh:
            detection_json = json.load(fh)
        db.ml_results.insert_one({
            "task_id": task_id,
            "filename": filename,
            "detection_json": detection_json,
            "created_at": datetime.utcnow(),
        })
        requests.post(
            Config.WEB_APP_CALLBACK_URL,
            json={"task_id": task_id, "status": "done"},
            timeout=10,
        )
    except Exception as exc:
        requests.post(
            Config.WEB_APP_CALLBACK_URL,
            json={"task_id": task_id, "status": "failed", "error": str(exc)},
            timeout=10,
        )


@app.route("/task", methods=["POST"])
def receive_task():
    payload = request.get_json(force=True)
    task_id = payload["task_id"]
    filename = payload["filename"]
    image_bytes = base64.b64decode(payload["image_b64"])
    threading.Thread(
        target=_run, args=(task_id, filename, image_bytes), daemon=True
    ).start()
    return {"task_id": task_id}, 202


if __name__ == "__main__":
    Config.RUNTIME_FOLDER.mkdir(parents=True, exist_ok=True)
    app.run(host="0.0.0.0", port=10990)
