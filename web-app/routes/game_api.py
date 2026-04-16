"""Game-related API routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from db.game_progress import get_progress, save_progress
from services.game_service import (
    CHALLENGES,
    get_default_progress,
    sanitize_progress,
)

game_bp = Blueprint("game_api", __name__)


@game_bp.route("/config", methods=["GET"])
def game_config():
    """Return challenge configuration and saved progress."""
    progress = sanitize_progress(get_progress())
    return jsonify(
        {
            "challenges": CHALLENGES,
            "progress": progress,
        }
    )


@game_bp.route("/save-progress", methods=["POST"])
def save_game_progress():
    """Save game progress to MongoDB."""
    payload = request.get_json(silent=True) or {}
    progress = sanitize_progress(payload)
    save_progress(progress)
    return jsonify({"status": "ok"}), 200


@game_bp.route("/reset", methods=["POST"])
def reset_game_progress():
    """Reset saved game progress to the initial state."""
    progress = get_default_progress()
    save_progress(progress)
    return jsonify({"status": "ok", "progress": progress}), 200
