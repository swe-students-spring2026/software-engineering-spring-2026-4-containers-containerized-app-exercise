"""
Pipeline for recording, transcription, analysis, and storage.
"""

import wave
from app.recorder import record_audio_manual
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


def run_pipeline() -> dict:
    """
    Run the full audio processing pipeline.

    Returns:
        Dictionary containing transcript and analysis results.
    """
    audio_path = record_audio_manual()
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


if __name__ == "__main__":
    output = run_pipeline()
    print(output)
