"""Tests for the ML Client"""

# pylint: disable=redefined-outer-name
# pylint: disable=import-error
# pylint: disable=wrong-import-position
import io
import sys
from unittest.mock import MagicMock
import pytest

sys.modules["whisper"] = MagicMock()
sys.modules["librosa"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["db"] = MagicMock()

from ml_client import (
    count_filler_words,
    compute_words_per_minute,
    rate_volume,
    rate_pitch,
    rate_pace,
    transcribe_audio,
    analyze_audio,
    app,
)


@pytest.fixture
def flask_client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


# Tests for count_filler_words
def test_count_filler_words_regular():
    """Testing regualar filler word counting"""
    assert count_filler_words("um I like uh saw like a tree") == 4


def test_count_filler_words_none():
    """Testing no filler word counting"""
    assert count_filler_words("I saw a tree") == 0


def test_count_filler_words_uppercase():
    """Testing uppercase filler word counting"""
    assert count_filler_words("UM I LIKE UH SAW A TREE") == 3


def test_count_filler_words_punct():
    """Testing punctuated filler word counting"""
    assert count_filler_words("um, I like saw uh a tree") == 3


def test_count_filler_words_empty():
    """Testing empty filler word counting"""
    assert count_filler_words("") == 0


# Tests for compute_words_per_minute
def test_compute_words_per_minute_regular():
    """Testing regular computing words per minutes"""
    assert compute_words_per_minute("hi hi hi hi", 4) == 60.0


def test_compute_words_per_minute_zero():
    """Testing computing words per minutes with no time"""
    assert compute_words_per_minute("hi hi hi hi", 0) == 0.0


def test_compute_words_per_minute_decimal():
    """Testing regular computing words per minutes"""
    assert compute_words_per_minute("hi hi hi hi hi hi", 4.5) == 80.0


# rate_volume tests
def test_rate_volume_too_quiet():
    """Test volume rated as too quiet"""
    assert rate_volume(-50) == "too quiet"


def test_rate_volume_too_loud():
    """Test volume rated as too loud"""
    assert rate_volume(-5) == "too loud"


def test_rate_volume_good():
    """Test volume rated as good"""
    assert rate_volume(-20) == "good"


# rate_pitch tests
def test_rate_pitch_monotone():
    """Test pitch rated as monotone"""
    assert rate_pitch(10) == "monotone"


def test_rate_pitch_too_varied():
    """Test pitch rated as too varied"""
    assert rate_pitch(3000) == "too varied"


def test_rate_pitch_good():
    """Test pitch rated as good"""
    assert rate_pitch(500) == "good"


# rate_pace tests
def test_rate_pace_too_slow():
    """Test pace rated as too slow"""
    assert rate_pace(80) == "too slow"


def test_rate_pace_too_fast():
    """Test pace rated as too fast"""
    assert rate_pace(191) == "too fast"


def test_rate_pace_good():
    """Test pace rated as good"""
    assert rate_pace(130) == "good"


# transcribe_audio test


def test_transcribe_audio_returns_text():
    """Test that transcribe_audio returns stripped transcript"""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "  um hello world  "}
    result = transcribe_audio("fake.wav", mock_model)
    assert result == "um hello world"


def test_transcribe_audio_empty():
    """Test that transcribe_audio handles empty transcript"""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "   "}
    result = transcribe_audio("fake.wav", mock_model)
    assert result == ""


# anaylze_audio tests


def test_analyze_audio_duration(mocker):
    """Test that analyze_audio returns correct duration"""
    mocker.patch("ml_client.librosa.load", return_value=(MagicMock(), 44100))
    mocker.patch("ml_client.librosa.get_duration", return_value=45.0)
    mocker.patch("ml_client.librosa.feature.rms", return_value=[[0.05] * 100])
    mocker.patch("ml_client.librosa.amplitude_to_db", return_value=-20.0)
    mocker.patch("ml_client.librosa.pyin", return_value=(MagicMock(), None, None))
    mocker.patch("ml_client.np.isnan", return_value=MagicMock())
    mocker.patch("ml_client.np.mean", return_value=0.05)
    mocker.patch("ml_client.np.var", return_value=500.0)

    result = analyze_audio("fake.wav")
    assert result["duration_seconds"] == 45.0


# flask route tests
def test_analyze_no_audio(flask_client):
    """Test analyze endpoint returns 400 when no audio file provided"""
    response = flask_client.post("/analyze")
    assert response.status_code == 400
    assert response.json["error"] == "no audio file"


def test_analyze_success(flask_client, mocker):
    """Test analyze endpoint returns 200 on success"""
    mocker.patch("ml_client.whisper.load_model", return_value=MagicMock())
    mocker.patch("ml_client.transcribe_audio", return_value="um hello world")
    mocker.patch(
        "ml_client.analyze_audio",
        return_value={
            "duration_seconds": 30.0,
            "avg_volume_db": -20.0,
            "pitch_variance": 500.0,
        },
    )
    mocker.patch("ml_client.speeches_collection.insert_one", return_value=MagicMock())
    data = {
        "audio": (io.BytesIO(b"fake audio content"), "audio_test.wav"),
        "title": "Test Speech",
        "user_id": "123",
    }
    response = flask_client.post(
        "/analyze", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.json["status"] == "success"
