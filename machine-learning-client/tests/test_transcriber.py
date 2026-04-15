from unittest.mock import patch, MagicMock
import pytest
import transcriber

def make_mock_response(json_data):
    mock = MagicMock()
    mock.json.return_value = json_data
    return mock

@patch("transcriber.requests.get")
@patch("transcriber.requests.post")
def test_transcriber_completed(mock_post, mock_get):
    mock_post.side_effect = [
        make_mock_response({"upload_url": "https://fake-url.com"}),
        make_mock_response({"id": "abc123"}),
    ]
    mock_get.return_value = make_mock_response({"status": "completed", "text": "hello world"})

    result = transcriber.transcribe_audio(b"fake audio")

    assert result == "hello world"

@patch("transcriber.requests.get")
@patch("transcriber.requests.post")
def test_transcriber_error(mock_post, mock_get):
    mock_post.side_effect = [
        make_mock_response({"upload_url": "https://fake-url.com"}),
        make_mock_response({"id": "abc123"}),
    ]
    mock_get.return_value = make_mock_response({"status": "error", "text": None, "error": "bad audio"})

    with pytest.raises(RuntimeError, match="Transcription failed: bad audio"):
        transcriber.transcribe_audio(b"fake audio")

@patch("transcriber.time.sleep", return_value=None)
@patch("transcriber.requests.get")
@patch("transcriber.requests.post")
def test_transcriber_processing(mock_post, mock_get, mock_sleep):
    mock_post.side_effect = [
        make_mock_response({"upload_url": "https://fake-url.com"}),
        make_mock_response({"id": "abc123"}),
    ]
    mock_get.side_effect = [
        make_mock_response({"status": "processing", "text": None}),
        make_mock_response({"status": "completed", "text": "final transcript"}),
    ]

    result = transcriber.transcribe_audio(b"fake audio")

    assert result == "final transcript"
    assert mock_sleep.call_count == 1