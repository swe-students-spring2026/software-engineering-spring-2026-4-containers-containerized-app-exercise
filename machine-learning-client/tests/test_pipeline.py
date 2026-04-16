"""Tests for app.pipeline."""

# pylint: disable=redefined-outer-name,too-few-public-methods

import sys
import types
import importlib
import pytest


@pytest.fixture
def pipeline_module(monkeypatch):
    """Load pipeline with a fake whisper module."""
    fake_whisper = types.SimpleNamespace(load_model=lambda _name: object())
    monkeypatch.setitem(sys.modules, "whisper", fake_whisper)

    for module_name in ["app.openai_transcriber", "app.pipeline"]:
        if module_name in sys.modules:
            del sys.modules[module_name]

    module = importlib.import_module("app.pipeline")
    return module


def test_get_wav_duration(monkeypatch, pipeline_module):
    """Test WAV duration calculation."""

    class FakeWave:
        """Fake wave file."""

        def getnframes(self):
            """Return fake frame count."""
            return 88200

        def getframerate(self):
            """Return fake frame rate."""
            return 44100

        def __enter__(self):
            """Enter context."""
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Exit context."""
            return False

    def fake_wave_open(*_args, **_kwargs):
        """Return fake wave object."""
        return FakeWave()

    monkeypatch.setattr(pipeline_module.wave, "open", fake_wave_open)

    duration = pipeline_module.get_wav_duration("fake.wav")

    assert duration == 2


def test_run_pipeline_happy_path(monkeypatch, pipeline_module):
    """Test full pipeline flow with mocked dependencies."""

    def fake_get_wav_duration(_path):
        """Return fake duration."""
        return 10

    def fake_transcribe_audio(_path):
        """Return fake transcript."""
        return "hello um world"

    def fake_analyze_transcript(_text, _duration):
        """Return fake transcript analysis."""
        return {
            "word_count": 3,
            "filler_words": {"um": 1},
            "total_filler_count": 1,
            "wpm": 18,
            "pace_feedback": "slowwww...",
            "filler_feedback": "Good fluency. Only a few filler words were used.",
        }

    def fake_save_practice_session(_session):
        """Return fake inserted id."""
        return "abc123"

    monkeypatch.setattr(pipeline_module, "get_wav_duration", fake_get_wav_duration)
    monkeypatch.setattr(pipeline_module, "transcribe_audio", fake_transcribe_audio)
    monkeypatch.setattr(
        pipeline_module,
        "analyze_transcript",
        fake_analyze_transcript,
    )
    monkeypatch.setattr(
        pipeline_module,
        "save_practice_session",
        fake_save_practice_session,
    )

    result = pipeline_module.run_pipeline("sample_audio/test.wav")

    assert result["audio_file"] == "sample_audio/test.wav"
    assert result["duration_seconds"] == 10
    assert result["transcript"] == "hello um world"
    assert result["analysis"]["word_count"] == 3
    assert result["analysis"]["total_filler_count"] == 1
    assert result["inserted_id"] == "abc123"


def test_run_pipeline_raises_for_empty_transcript(monkeypatch, pipeline_module):
    """Test empty transcript raises ValueError."""

    def fake_get_wav_duration(_path):
        """Return fake duration."""
        return 10

    def fake_transcribe_audio(_path):
        """Return blank transcript."""
        return "   "

    monkeypatch.setattr(pipeline_module, "get_wav_duration", fake_get_wav_duration)
    monkeypatch.setattr(pipeline_module, "transcribe_audio", fake_transcribe_audio)

    with pytest.raises(ValueError, match="No speech was detected"):
        pipeline_module.run_pipeline("sample_audio/test.wav")


def test_process_commands_handles_success(monkeypatch, pipeline_module):
    """Test process_commands updates command status to done after success."""
    updates = []

    class FakeCommands:
        """Fake commands collection."""

        def __init__(self):
            """Initialize fake command state."""
            self.called = False

        def find_one(self, _query):
            """Return one fake pending command."""
            if self.called:
                raise KeyboardInterrupt
            self.called = True
            return {
                "_id": "cmd1",
                "status": "pending",
                "action": "process_audio",
                "audio_file": "sample_audio/test.wav",
            }

        def update_one(self, query, update):
            """Record updates."""
            updates.append((query, update))

    class FakeDatabase:
        """Fake database wrapper."""

        def __init__(self):
            """Initialize fake database."""
            self.commands = FakeCommands()

    class FakeClient:
        """Fake Mongo client."""

        def __getitem__(self, _name):
            """Return fake database."""
            return FakeDatabase()

    def fake_mongo_client(_uri):
        """Return fake Mongo client."""
        return FakeClient()

    def fake_run_pipeline(_audio_path):
        """Return fake pipeline result."""
        return {"inserted_id": "result123"}

    def fake_sleep(_seconds):
        """Do nothing."""
        return None

    monkeypatch.setattr(pipeline_module, "MongoClient", fake_mongo_client)
    monkeypatch.setattr(pipeline_module, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(pipeline_module.time, "sleep", fake_sleep)

    try:
        pipeline_module.process_commands()
    except KeyboardInterrupt:
        pass

    assert updates[0][0] == {"_id": "cmd1"}
    assert updates[0][1] == {
        "$set": {
            "status": "done",
            "result_id": "result123",
        }
    }


def test_process_commands_handles_error(monkeypatch, pipeline_module):
    """Test process_commands updates command status to error after failure."""
    updates = []

    class FakeCommands:
        """Fake commands collection."""

        def __init__(self):
            """Initialize fake command state."""
            self.called = False

        def find_one(self, _query):
            """Return one fake pending command."""
            if self.called:
                raise KeyboardInterrupt
            self.called = True
            return {
                "_id": "cmd2",
                "status": "pending",
                "action": "process_audio",
                "audio_file": "bad.wav",
            }

        def update_one(self, query, update):
            """Record updates."""
            updates.append((query, update))

    class FakeDatabase:
        """Fake database wrapper."""

        def __init__(self):
            """Initialize fake database."""
            self.commands = FakeCommands()

    class FakeClient:
        """Fake Mongo client."""

        def __getitem__(self, _name):
            """Return fake database."""
            return FakeDatabase()

    def fake_mongo_client(_uri):
        """Return fake Mongo client."""
        return FakeClient()

    def fake_run_pipeline(_audio_path):
        """Raise fake pipeline error."""
        raise ValueError("No speech was detected in the recording")

    def fake_sleep(_seconds):
        """Do nothing."""
        return None

    monkeypatch.setattr(pipeline_module, "MongoClient", fake_mongo_client)
    monkeypatch.setattr(pipeline_module, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(pipeline_module.time, "sleep", fake_sleep)

    try:
        pipeline_module.process_commands()
    except KeyboardInterrupt:
        pass

    assert updates[0][0] == {"_id": "cmd2"}
    assert updates[0][1] == {
        "$set": {
            "status": "error",
            "error": "No speech was detected in the recording",
        }
    }
