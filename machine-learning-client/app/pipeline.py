"""
Pipeline for transcription, analysis, and storage.
"""

import time
import wave
from pymongo import MongoClient
from app.config import MONGO_URI, MONGO_DB_NAME
from app.openai_transcriber import transcribe_audio
from app.data_analyzer import analyze_transcript
from app.db import save_practice_session


def get_wav_duration(file_path: str) -> float:
    """
    Get duration of a WAV audio file in seconds.

    Args:
        file_path: Path to the WAV file.

    Returns:
        Duration in seconds.
    """
    with wave.open(file_path, "rb") as wav_file:
        frames = wav_file.getnframes()
        sample_rate = wav_file.getframerate()
        duration = frames / float(sample_rate)

    return round(duration)


def run_pipeline(audio_path: str) -> dict:
    """
    Run the full audio processing pipeline.

    Args:
        audio_path: Path to the audio file.

    Returns:
        Dictionary containing transcript and analysis results.
    """
    print(f"Using audio file: {audio_path}")

    duration_seconds = get_wav_duration(audio_path)
    transcript = transcribe_audio(audio_path)
    analysis = analyze_transcript(transcript, duration_seconds)

    session = {
        "audio_file": audio_path,
        "duration_seconds": duration_seconds,
        "transcript": transcript,
        "analysis": analysis,
    }

    inserted_id = save_practice_session(session)
    session["inserted_id"] = str(inserted_id)

    return session


def process_commands():
    """
    Continuously watch the commands collection for pending audio jobs.
    """
    client = MongoClient(MONGO_URI)
    database = client[MONGO_DB_NAME]

    print("ML client listening for commands...")

    while True:
        command = database.commands.find_one({"status": "pending"})

        if command and command.get("action") == "process_audio":
            audio_path = command["audio_file"]

            try:
                result = run_pipeline(audio_path)
                print(result)

                database.commands.update_one(
                    {"_id": command["_id"]},
                    {
                        "$set": {
                            "status": "done",
                            "result_id": result["inserted_id"],
                        }
                    },
                )

            except Exception as error:
                database.commands.update_one(
                    {"_id": command["_id"]},
                    {"$set": {"status": "error", "error": str(error)}},
                )

        time.sleep(2)


if __name__ == "__main__":
    process_commands()