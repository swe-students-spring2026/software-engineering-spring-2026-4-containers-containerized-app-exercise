"""
Audio recording utilities.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

from app.config import CHANNELS, SAMPLE_RATE

OUTPUT_DIR = Path("record_outputs")


def record_audio_manual(
    sample_rate: int = SAMPLE_RATE,
    channels: int = CHANNELS,
) -> str:
    """
    Record audio from the default microphone until the user stops it.

    Args:
        sample_rate: Sampling rate in Hz.
        channels: Number of audio channels.

    Returns:
        Path to the saved audio file.
    """
    if sample_rate <= 0:
        raise ValueError("sample_rate must be greater than 0")
    if channels <= 0:
        raise ValueError("channels must be greater than 0")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_file = OUTPUT_DIR / f"record_{timestamp}.wav"

    frames = []

    def callback(indata, frames_count, time, status):
        if status:
            print(status)
        frames.append(indata.copy())

    input("Press Enter to start recording...")
    print("Recording... Press Enter again to stop.")

    with sd.InputStream(
        samplerate=sample_rate,
        channels=channels,
        dtype="int16",
        callback=callback,
    ):
        input()

    recording = np.concatenate(frames, axis=0)
    write(output_file, sample_rate, recording)

    print(f"Audio saved to {output_file}")
    return str(output_file)
