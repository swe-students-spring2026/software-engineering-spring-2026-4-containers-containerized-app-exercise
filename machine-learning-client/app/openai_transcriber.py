"""
Local Whisper speech-to-text helper.
"""

from pathlib import Path

import whisper


MODEL_NAME = "base"
_model = None


def get_model():
    """
    Lazily load the Whisper model once.

    Returns:
        Loaded Whisper model.
    """
    global _model
    if _model is None:
        _model = whisper.load_model(MODEL_NAME)
    return _model


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe an audio file using local Whisper.

    Args:
        file_path: Path to the audio file.

    Returns:
        Transcribed text.

    Raises:
        ValueError: If file path does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"Audio file not found: {file_path}")

    model = get_model()
    result = model.transcribe(str(path))

    text = result.get("text", "").strip()
    return text
