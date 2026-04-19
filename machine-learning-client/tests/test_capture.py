"""Unit tests for the capture script."""

from unittest.mock import patch

from app.capture import main


@patch("app.capture.capture_image")
def test_main(mock_capture):
    """Test the main capture script execution."""
    mock_capture.return_value = "fake_path.jpg"
    main()
    mock_capture.assert_called_once()
