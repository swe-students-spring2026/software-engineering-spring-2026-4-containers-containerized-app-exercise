"""Main application module for the web app."""

import os
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, render_template
from db import get_db

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    """Retrieve all practice sessions from the database."""
    database = get_db()
    sessions = list(database.practice_sessions.find({}, {"_id": 0}))
    return jsonify(sessions), 200


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session_details(session_id):
    """Retrieve details for a specific practice session by its ID."""
    database = get_db()
    session = database.practice_sessions.find_one(
        {"session_id": session_id}, {"_id": 0}
    )
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session), 200


@app.route("/api/trigger-practice", methods=["POST"])
def trigger_practice():
    """Trigger a new practice session by issuing a command to the database."""
    database = get_db()
    command = {"action": "start_listening", "status": "pending"}
    database.commands.insert_one(command)
    return jsonify({"message": "Practice session triggered."}), 202

@app.route("/api/upload-audio", methods=["POST"])
def upload_audio():
    """Upload an audio file and queue it for processing."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files["audio"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    database = get_db()
    command = {
        "action": "process_audio",
        "audio_file": save_path,
        "status": "pending",
    }
    database.commands.insert_one(command)

    return jsonify({"message": "Audio uploaded and queued."}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
