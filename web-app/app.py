"""Main application module for the web app."""

import uuid
import os
from flask import Flask, jsonify, request, render_template
from db import get_db
from pydub import AudioSegment
from bson import ObjectId

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static",
)

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def _serialize_mongo_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON serializable dict"""
    if not doc:
        return doc
    out = dict(doc)
    if "_id" in out:
        out["_id"] = str(out["_id"])
    return out


@app.route("/")
def home():
    """Render the index HTML page."""
    return render_template("index.html")


@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    """Retrieve all practice sessions from the database."""
    database = get_db()
    sessions = list(database.practice_sessions.find({}))
    return jsonify([_serialize_mongo_doc(s) for s in sessions]), 200


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session_details(session_id):
    """Retrieve details for a specific practice session by its ID."""
    database = get_db()
    oid = ObjectId(session_id)
    session = database.practice_sessions.find_one({"_id": oid})
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(_serialize_mongo_doc(session)), 200


@app.route("/api/commands/<command_id>", methods=["GET"])
def get_command_status(command_id):
    """Retrieve the status of a queued/processing command."""
    database = get_db()
    oid = ObjectId(command_id)
    command = database.commands.find_one({"_id": oid})
    return jsonify(_serialize_mongo_doc(command)), 200


@app.route("/api/trigger-practice", methods=["POST"])
def trigger_practice():
    """Trigger a new practice session by issuing a command to the database."""
    database = get_db()
    command = {"action": "start_listening", "status": "pending"}
    database.commands.insert_one(command)
    return (
        jsonify({"message": "Practice session triggered."}),
        202,
    )


@app.route("/api/upload-audio", methods=["POST"])
def upload_audio():
    """Upload an audio file, convert to WAV, and queue it for processing."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files["audio"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # generate unique filenames
    unique_id = str(uuid.uuid4())
    webm_filename = f"{unique_id}.webm"
    wav_filename = f"{unique_id}.wav"

    webm_path = os.path.join(UPLOAD_FOLDER, webm_filename)
    wav_path = os.path.join(UPLOAD_FOLDER, wav_filename)

    # save original file
    file.save(webm_path)

    try:
        # convert to WAV
        audio = AudioSegment.from_file(webm_path, format="webm")
        audio.export(wav_path, format="wav")
    except Exception as e:  # pylint: disable=broad-exception-caught
        return (
            jsonify({"error": f"Conversion failed: {str(e)}"}),
            500,
        )

    database = get_db()

    command = {
        "action": "process_audio",
        "audio_file": wav_path,
        "status": "pending",
    }

    inserted = database.commands.insert_one(command)

    return (
        jsonify(
            {
                "message": "Audio uploaded, converted, and queued.",
                "wav_file": wav_path,
                "command_id": str(inserted.inserted_id),
            }
        ),
        202,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
