"""Machine learning client for audio speech analysis."""

# pylint: disable=import-error
import re
import uuid
from datetime import datetime
import librosa
import numpy as np
import whisper
from flask import Flask, request, jsonify
from db import speeches_collection

app = Flask(__name__)
FILLER_WORDS = {"um", "uh", "like"}


def count_filler_words(transcript):
    """Count the number of filler words in a transcript."""
    total = 0
    transcript_lower = transcript.lower()
    transcript_clean = re.sub(r"[^\w\s]", "", transcript_lower)
    for words in FILLER_WORDS:
        count = transcript_clean.split().count(words)
        total += count
    return total


def transcribe_audio(audio_path, model):
    """Transcribe audio file using Whisper model."""
    transcript_result = model.transcribe(audio_path, initial_prompt="Um, uh, like")
    return transcript_result["text"].strip()


def compute_words_per_minute(transcript, duration_seconds):
    """Compute words per minute from transcript and duration."""
    if duration_seconds <= 0:
        return 0.0
    word_count = len(transcript.split())
    return round((word_count / duration_seconds) * 60, 2)


def analyze_audio(audio_path):
    """Analyze audio file and return acoustic features."""
    y, sr = librosa.load(audio_path, sr=None)
    duration_seconds = librosa.get_duration(y=y, sr=sr)

    rms = librosa.feature.rms(y=y)[0]
    avg_volume_db = round(float(librosa.amplitude_to_db(np.mean(rms))), 2)

    f0, _, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
    )
    voiced_f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
    pitch_variance = round(float(np.var(voiced_f0)) if len(voiced_f0) > 0 else 0.0, 4)

    return {
        "duration_seconds": round(duration_seconds, 2),
        "avg_volume_db": avg_volume_db,
        "pitch_variance": pitch_variance,
    }


def rate_volume(avg_vol_db):
    """Gives the volume of the speech a rating"""
    if avg_vol_db < -40:
        return "too quiet"
    if avg_vol_db > -10:
        return "too loud"
    return "good"


def rate_pitch(pitch_var):
    """Gives the pitch variance of the speech a rating"""
    if pitch_var < 50:
        return "monotone"
    if pitch_var > 2000:
        return "too varied"
    return "good"


def rate_pace(pace):
    """Gives the pace of the speech a rating"""
    if pace < 100:
        return "too slow"
    if pace > 190:
        return "too fast"
    return "good"


@app.route("/analyze", methods=["POST"])
def analyze():
    """Recieve audio files and run speech analysis"""
    if "audio" not in request.files:
        return jsonify({"error": "no audio file"}), 400
    audio_file = request.files["audio"]
    audio_path = f"/tmp/{uuid.uuid4()}_{audio_file.filename}"
    audio_file.save(audio_path)

    model = whisper.load_model("base")

    transcript = transcribe_audio(audio_path, model)
    acoustic = analyze_audio(audio_path)
    filler = count_filler_words(transcript)
    wpm = compute_words_per_minute(transcript, acoustic["duration_seconds"])
    volume_rating = rate_volume(acoustic["avg_volume_db"])
    pitch_rating = rate_pitch(acoustic["pitch_variance"])
    pace_rating = rate_pace(wpm)

    result = {
        "user_id": request.form.get("user_id"),
        "title": request.form.get("title"),
        "timestamp": datetime.utcnow(),
        "transcript": transcript,
        "wpm": wpm,
        "filler_count": filler,
        "volume_rating": volume_rating,
        "pitch_rating": pitch_rating,
        "pace_rating": pace_rating,
    }
    speeches_collection.insert_one(result)
    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
