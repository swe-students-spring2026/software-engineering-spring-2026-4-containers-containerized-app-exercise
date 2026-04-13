import re
import sys
import librosa
import numpy as np
import whisper

FILLER_WORDS = {"um", "uh", "like"}


def count_filler_words(transcript):
    total = 0
    transcript_lower = transcript.lower()
    transcript_clean = re.sub(r"[^\w\s]", "", transcript_lower)
    for words in FILLER_WORDS:
        count = transcript_clean.split().count(words)
        total += count
    return total


def transcribe_audio(audio_path, model):
    transcript_result = model.transcribe(audio_path, initial_prompt="Um, uh, like")
    return transcript_result["text"].strip()


def compute_words_per_minute(transcript, duration_seconds):
    if duration_seconds <= 0:
        return 0.0
    word_count = len(transcript.split())
    return round((word_count / duration_seconds) * 60, 2)


def analyze_audio(audio_path):
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


def run_test(audio_path):
    model = whisper.load_model("base")
    print("whisper model loaded\n")

    transcript = transcribe_audio(audio_path, model)
    print(f"transcrpt: {transcript}\n")

    print("Analyzing audio with librosa...")
    acoustic = analyze_audio(audio_path)
    filler = count_filler_words(transcript)
    wpm = compute_words_per_minute(transcript, acoustic["duration_seconds"])

    print("--- RESULTS ---")
    print(f"Duration:          {acoustic['duration_seconds']}s")
    print(f"Words per minute:  {wpm}")
    print(f"Avg volume:        {acoustic['avg_volume_db']} dB")
    print(f"Pitch variance:    {acoustic['pitch_variance']}")
    print(f"Filler word total: {filler}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pipenv run python test_ml.py <path_to_audio_file>")
        print("Example: pipenv run python test_ml.py test_audio.wav")
        sys.exit(1)
    run_test(sys.argv[1])
