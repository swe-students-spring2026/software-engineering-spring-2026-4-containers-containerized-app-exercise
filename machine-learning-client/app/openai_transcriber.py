"""
Local Whisper speech-to-text helper.
"""

from pathlib import Path
import whisper

MODEL_NAME = "base.en"


def get_model():
    """
    Lazily load the Whisper model once.

    Returns:
        Loaded Whisper model.
    """
    model = whisper.load_model(MODEL_NAME)
    return model


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

    print("Transcribing file:", path)

    model = get_model()
    result = model.transcribe(str(path))

    print("Whisper raw result:", result)

    text = result.get("text", "").strip()
    print("Whisper text repr:", repr(text))

    return text
