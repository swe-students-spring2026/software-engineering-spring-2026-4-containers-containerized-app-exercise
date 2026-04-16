"""Tests for app.pipeline."""

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
            return 88200

        def getframerate(self):
            return 44100

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

    monkeypatch.setattr(
        pipeline_module.wave,
        "open",
        lambda *_args, **_kwargs: FakeWave(),
    )

    duration = pipeline_module.get_wav_duration("fake.wav")

    assert duration == 2


def test_run_pipeline_happy_path(monkeypatch, pipeline_module):
    """Test full pipeline flow with mocked dependencies."""
    monkeypatch.setattr(pipeline_module, "get_wav_duration", lambda _path: 10)
    monkeypatch.setattr(
        pipeline_module,
        "transcribe_audio",
        lambda _path: "hello um world",
    )
    monkeypatch.setattr(
        pipeline_module,
        "analyze_transcript",
        lambda _text, _duration: {
            "word_count": 3,
            "filler_words": {"um": 1},
            "total_filler_count": 1,
            "wpm": 18,
            "pace_feedback": "slowwww...",
            "filler_feedback": "Good fluency. Only a few filler words were used.",
        },
    )
    monkeypatch.setattr(
        pipeline_module,
        "save_practice_session",
        lambda _session: "abc123",
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
    monkeypatch.setattr(pipeline_module, "get_wav_duration", lambda _path: 10)
    monkeypatch.setattr(pipeline_module, "transcribe_audio", lambda _path: "   ")

    with pytest.raises(ValueError, match="No speech was detected"):
        pipeline_module.run_pipeline("sample_audio/test.wav")


def test_process_commands_handles_success(monkeypatch, pipeline_module):
    """Test process_commands updates command status to done after success."""
    updates = []

    class FakeCommands:
        """Fake commands collection."""

        def __init__(self):
            self.called = False

        def find_one(self, _query):
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
            updates.append((query, update))

    class FakeDatabase:
        """Fake database wrapper."""

        def __init__(self):
            self.commands = FakeCommands()

    class FakeClient:
        """Fake Mongo client."""

        def __getitem__(self, _name):
            return FakeDatabase()

    monkeypatch.setattr(pipeline_module, "MongoClient", lambda _uri: FakeClient())
    monkeypatch.setattr(
        pipeline_module,
        "run_pipeline",
        lambda _audio_path: {"inserted_id": "result123"},
    )
    monkeypatch.setattr(pipeline_module.time, "sleep", lambda _seconds: None)

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
            self.called = False

        def find_one(self, _query):
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
            updates.append((query, update))

    class FakeDatabase:
        """Fake database wrapper."""

        def __init__(self):
            self.commands = FakeCommands()

    class FakeClient:
        """Fake Mongo client."""

        def __getitem__(self, _name):
            return FakeDatabase()

    def fake_run_pipeline(_audio_path):
        raise ValueError("No speech was detected in the recording")

    monkeypatch.setattr(pipeline_module, "MongoClient", lambda _uri: FakeClient())
    monkeypatch.setattr(pipeline_module, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(pipeline_module.time, "sleep", lambda _seconds: None)

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