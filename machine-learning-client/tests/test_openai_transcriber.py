"""Tests for app.openai_transcriber."""

import sys
import types
import importlib
import pytest


@pytest.fixture
def transcriber_module(monkeypatch):
    """Load openai_transcriber with a fake whisper module."""
    fake_whisper = types.SimpleNamespace(load_model=lambda _name: object())
    monkeypatch.setitem(sys.modules, "whisper", fake_whisper)

    if "app.openai_transcriber" in sys.modules:
        del sys.modules["app.openai_transcriber"]

    module = importlib.import_module("app.openai_transcriber")
    return module


def test_transcribe_audio_missing_file(transcriber_module):
    """Test that a missing file raises ValueError."""
    with pytest.raises(ValueError):
        transcriber_module.transcribe_audio("does_not_exist.wav")


def test_transcribe_audio_returns_stripped_text(
    monkeypatch, tmp_path, transcriber_module
):
    """Test transcription returns stripped text."""
    audio_file = tmp_path / "test.wav"
    audio_file.write_text("fake audio", encoding="utf-8")

    class FakeModel:
        """Fake Whisper model."""

        def transcribe(self, _path):
            return {"text": "  hello world  "}

    monkeypatch.setattr(transcriber_module, "get_model", lambda: FakeModel())

    result = transcriber_module.transcribe_audio(str(audio_file))

    assert result == "hello world"


def test_transcribe_audio_returns_empty_string_when_text_missing(
    monkeypatch, tmp_path, transcriber_module
):
    """Test transcription returns empty string if text is missing."""
    audio_file = tmp_path / "test.wav"
    audio_file.write_text("fake audio", encoding="utf-8")

    class FakeModel:
        """Fake Whisper model."""

        def transcribe(self, _path):
            return {}

    monkeypatch.setattr(transcriber_module, "get_model", lambda: FakeModel())

    result = transcriber_module.transcribe_audio(str(audio_file))

    assert result == ""