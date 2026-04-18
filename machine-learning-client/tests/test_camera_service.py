"""Unit tests for the camera service."""

from unittest.mock import MagicMock, patch

import pytest

from app.camera_service import capture_image


@patch("app.camera_service.cv2")
@patch("app.camera_service.time.sleep")
@patch("app.camera_service.os.makedirs")
def test_capture_image_success(mock_makedirs, mock_sleep, mock_cv2):
    """Test a successful image capture."""
    # Set up our mock camera simulation
    mock_camera = MagicMock()
    mock_camera.isOpened.return_value = True
    mock_camera.read.return_value = (True, "fake_frame_data")

    mock_cv2.VideoCapture.return_value = mock_camera
    mock_cv2.imwrite.return_value = True

    # Run the function
    result = capture_image("test_output")

    # Assert it behaved correctly
    assert "test_output/scan_" in result
    assert result.endswith(".jpg")
    mock_makedirs.assert_called_once_with("test_output", exist_ok=True)
    mock_sleep.assert_called_once_with(2)


@patch("app.camera_service.cv2")
@patch("app.camera_service.time.sleep")
@patch("app.camera_service.os.makedirs")
def test_capture_image_not_opened(mock_makedirs, mock_sleep, mock_cv2):
    """Test when the camera fails to open."""
    mock_camera = MagicMock()
    mock_camera.isOpened.return_value = False
    mock_cv2.VideoCapture.return_value = mock_camera

    with pytest.raises(RuntimeError, match="Could not open camera"):
        capture_image()

    mock_makedirs.assert_called_once()
    mock_sleep.assert_not_called()


@patch("app.camera_service.cv2")
@patch("app.camera_service.time.sleep")
@patch("app.camera_service.os.makedirs")
def test_capture_image_read_fails(mock_makedirs, mock_sleep, mock_cv2):
    """Test when the camera fails to read a frame."""
    mock_camera = MagicMock()
    mock_camera.isOpened.return_value = True
    mock_camera.read.return_value = (False, None)
    mock_cv2.VideoCapture.return_value = mock_camera

    with pytest.raises(RuntimeError, match="Could not capture image"):
        capture_image()

    mock_makedirs.assert_called_once()
    mock_sleep.assert_called_once()


@patch("app.camera_service.cv2")
@patch("app.camera_service.time.sleep")
@patch("app.camera_service.os.makedirs")
def test_capture_image_save_fails(mock_makedirs, mock_sleep, mock_cv2):
    """Test when the image fails to save to disk."""
    mock_camera = MagicMock()
    mock_camera.isOpened.return_value = True
    mock_camera.read.return_value = (True, "fake_frame_data")
    mock_cv2.VideoCapture.return_value = mock_camera
    mock_cv2.imwrite.return_value = False

    with pytest.raises(RuntimeError, match="Could not save image"):
        capture_image()

    mock_makedirs.assert_called_once()
    mock_sleep.assert_called_once()
