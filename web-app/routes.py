import base64
import uuid
from datetime import datetime

import requests
from flask import Blueprint, redirect, render_template, request, url_for

from config import Config
from db import get_db
from services import (
    allowed_file,
    get_inventory_items,
    save_detection_results_to_db,
    save_uploaded_file,
    soft_delete_inventory_item,
    update_inventory_item_name,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("index.html")


@main_bp.route("/dashboard")
def dashboard():
    items = get_inventory_items()
    return render_template("dashboard.html", items=items)


@main_bp.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return "No file part in request", 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return "No selected file", 400
    if not allowed_file(image_file.filename):
        return "Unsupported file type", 400

    task_id = uuid.uuid4().hex
    saved_filename, saved_path = save_uploaded_file(image_file)

    get_db().uploads.insert_one({
        "task_id": task_id,
        "filename": saved_filename,
        "status": "pending",
        "created_at": datetime.utcnow(),
    })

    with open(saved_path, "rb") as fh:
        image_b64 = base64.b64encode(fh.read()).decode()

    requests.post(
        f"{Config.ML_SERVICE_URL}/task",
        json={"task_id": task_id, "filename": saved_filename, "image_b64": image_b64},
        timeout=10,
    )

    return redirect(url_for("main.dashboard"))


@main_bp.route("/ml-callback", methods=["POST"])
def ml_callback():
    payload = request.get_json(force=True)
    task_id = payload["task_id"]
    if payload.get("status") == "done":
        save_detection_results_to_db(task_id)
    else:
        get_db().uploads.update_one(
            {"task_id": task_id},
            {"$set": {"status": "failed", "error": payload.get("error")}},
        )
    return "", 200


@main_bp.route("/items/<item_id>/edit", methods=["POST"])
def edit_item(item_id):
    new_name = request.form.get("display_name", "").strip()

    if new_name:
        update_inventory_item_name(item_id, new_name)

    return redirect(url_for("main.dashboard"))


@main_bp.route("/items/<item_id>/delete", methods=["POST"])
def delete_item(item_id):
    soft_delete_inventory_item(item_id)
    return redirect(url_for("main.dashboard"))
