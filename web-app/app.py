"""Main application module for the web app."""

from flask import Flask, jsonify
from db import get_db

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
