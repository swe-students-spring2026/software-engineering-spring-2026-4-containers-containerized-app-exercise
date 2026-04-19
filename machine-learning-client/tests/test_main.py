"""Unit tests for ML client main logic."""

import datetime
from unittest.mock import MagicMock, patch

import main  # pylint: disable=import-error


def test_distraction_classification():
    """Test the distraction_classification function logic."""
    assert main.distraction_classification(None) == "absent"

    assert main.distraction_classification(("happy", 0.9)) == "focused"
    assert main.distraction_classification(("neutral", 0.9)) == "focused"
    assert main.distraction_classification(("angry", 0.9)) == "focused"

    assert main.distraction_classification(("sad", 0.9)) == "distracted"
    assert main.distraction_classification(("fear", 0.9)) == "distracted"
    assert main.distraction_classification(("disgust", 0.9)) == "distracted"
    assert main.distraction_classification(("surprise", 0.9)) == "distracted"

    assert main.distraction_classification(("unknown_emotion", 0.9)) == "unknown"


@patch("main.FER")
@patch("main.cv2.VideoCapture")
def test_get_face_emotion_success(mock_video_capture, mock_fer):
    """Test get_face_emotion when face is successfully detected."""
    # Setup mock VideoCapture
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, "fake_img_data")
    mock_video_capture.return_value = mock_cap

    # Setup mock FER detector
    mock_detector = MagicMock()
    mock_detector.top_emotion.return_value = ("happy", 0.95)
    mock_fer.return_value = mock_detector

    img_data, result = main.get_face_emotion()

    assert img_data == "fake_img_data"
    assert result == ("happy", 0.95)
    mock_detector.detect_emotions.assert_called_once_with("fake_img_data")
    mock_detector.top_emotion.assert_called_once_with("fake_img_data")


@patch("main.FER")
@patch("main.cv2.VideoCapture")
@patch("main.os.path.exists")
@patch("main.cv2.imread")
def test_get_face_emotion_fallback(
    mock_imread, mock_exists, mock_video_capture, mock_fer
):
    """Test get_face_emotion when VideoCapture fails and uses fallback."""
    # Setup mock VideoCapture to fail
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False
    mock_video_capture.return_value = mock_cap

    # Setup mock fallback image
    mock_exists.return_value = True
    mock_imread.return_value = "fallback_img_data"

    # Setup mock FER detector
    mock_detector = MagicMock()
    mock_detector.top_emotion.return_value = ("neutral", 0.88)
    mock_fer.return_value = mock_detector

    img_data, result = main.get_face_emotion()

    assert img_data == "fallback_img_data"
    assert result == ("neutral", 0.88)
    mock_detector.detect_emotions.assert_called_once_with("fallback_img_data")


@patch("main.get_collection")
@patch("main.save_snapshot")
@patch("main.cv2.imencode")
def test_store_data_active_session(
    mock_imencode, mock_save_snapshot, mock_get_collection
):
    """Test store_data when an active session exists."""
    # Setup active session mock
    mock_sessions_col = MagicMock()
    mock_active_session = {"_id": "session123", "user_id": "user456"}
    mock_sessions_col.find_one.return_value = mock_active_session
    mock_get_collection.return_value = mock_sessions_col

    # Setup imencode mock
    mock_buffer = MagicMock()
    mock_buffer.tobytes.return_value = b"fake_image_bytes"
    mock_imencode.return_value = (True, mock_buffer)

    main.store_data("fake_frame", "happy", 0.95, "focused")

    # Verify save_snapshot was called correctly
    assert mock_save_snapshot.call_count == 1
    snapshot_arg = mock_save_snapshot.call_args[0][0]
    assert snapshot_arg["user_id"] == "user456"
    assert snapshot_arg["session_id"] == "session123"
    assert snapshot_arg["emotion"] == "happy"
    assert snapshot_arg["confidence"] == 0.95
    assert snapshot_arg["classification"] == "focused"
    assert snapshot_arg["image"] == b"fake_image_bytes"
    assert isinstance(snapshot_arg["timestamp"], datetime.datetime)

    # Verify session snapshot_count was incremented
    mock_sessions_col.update_one.assert_called_once_with(
        {"_id": "session123"}, {"$inc": {"snapshot_count": 1}}
    )


@patch("main.get_collection")
@patch("main.save_snapshot")
def test_store_data_no_active_session(mock_save_snapshot, mock_get_collection):
    """Test store_data when no active session exists."""
    mock_sessions_col = MagicMock()
    mock_sessions_col.find_one.return_value = None
    mock_get_collection.return_value = mock_sessions_col

    main.store_data("fake_frame", "happy", 0.95, "focused")

    mock_save_snapshot.assert_not_called()
