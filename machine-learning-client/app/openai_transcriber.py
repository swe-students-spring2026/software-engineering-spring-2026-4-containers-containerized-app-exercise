"""
OpenAI speech-to-text helper.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(file_path: str, model: str = "gpt-4o-mini-transcribe") -> str:
    """
    Transcribe an audio file using OpenAI speech-to-text API.

    Args:
        file_path: Path to the audio file.
        model: OpenAI transcription model.

    Returns:
        Transcribed text.

    Raises:
        ValueError: If file path does not exist.
        RuntimeError: If API key is missing.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")

    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"Audio file not found: {file_path}")

    with path.open("rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
        )

    return transcript.text