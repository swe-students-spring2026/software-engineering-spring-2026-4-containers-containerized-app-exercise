"""Unit tests for ml_client and database modules."""

from unittest.mock import MagicMock, patch
import pytest

from ml_client import capture_image, run_inference, process_once
from database import save_result


# ── capture_image ──────────────────────────────────────────

class TestCaptureImage:
    """Tests for capture_image()."""

    @patch("ml_client.cv2.VideoCapture")
    def test_capture_success(self, mock_cap_class, tmp_path):
        """Should save image and return path on success."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())
        mock_cap_class.return_value = mock_cap

        output = tmp_path / "out.jpg"
        with patch("ml_client.cv2.imwrite"):
            result = capture_image(str(output))

        assert result == str(output)

    @patch("ml_client.cv2.VideoCapture")
    def test_capture_camera_not_opened(self, mock_cap_class):
        """Should return None if camera cannot be opened."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cap_class.return_value = mock_cap

        result = capture_image()
        assert result is None

    @patch("ml_client.cv2.VideoCapture")
    def test_capture_read_fails(self, mock_cap_class):
        """Should return None if frame read fails."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_cap_class.return_value = mock_cap

        result = capture_image()
        assert result is None


# ── run_inference ──────────────────────────────────────────

class TestRunInference:
    """Tests for run_inference()."""

    @patch("ml_client.Roboflow")
    def test_returns_predictions(self, mock_rf):
        """Should return list of predictions from Roboflow."""
        mock_model = MagicMock()
        mock_model.predict.return_value.json.return_value = {
            "predictions": [
                {"class": "PLASTIC", "confidence": 0.91},
                {"class": "GLASS", "confidence": 0.75},
            ]
        }
        mock_rf.return_value.workspace.return_value\
            .project.return_value.version.return_value\
            .model = mock_model

        result = run_inference("test.jpg")
        assert len(result) == 2
        assert result[0]["class"] == "PLASTIC"

    @patch("ml_client.Roboflow")
    def test_empty_predictions(self, mock_rf):
        """Should return empty list when nothing detected."""
        mock_model = MagicMock()
        mock_model.predict.return_value.json.return_value = {
            "predictions": []
        }
        mock_rf.return_value.workspace.return_value\
            .project.return_value.version.return_value\
            .model = mock_model

        result = run_inference("test.jpg")
        assert result == []


# ── save_result ────────────────────────────────────────────

class TestSaveResult:
    """Tests for database.save_result()."""

    def test_saves_document(self):
        """Should insert a document and return an id."""
        mock_collection = MagicMock()
        mock_collection.insert_one.return_value.inserted_id = "abc123"

        predictions = [{"class": "PLASTIC", "confidence": 0.88}]
        doc_id = save_result(mock_collection, "test.jpg", predictions)

        assert doc_id == "abc123"
        mock_collection.insert_one.assert_called_once()

    def test_document_structure(self):
        """Saved document should contain required fields."""
        mock_collection = MagicMock()
        mock_collection.insert_one.return_value.inserted_id = "xyz"

        predictions = [{"class": "METAL", "confidence": 0.76}]
        save_result(mock_collection, "img.jpg", predictions)

        doc = mock_collection.insert_one.call_args[0][0]
        assert "timestamp" in doc
        assert "image_path" in doc
        assert "predictions" in doc
        assert "classes_detected" in doc
        assert "prediction_count" in doc


# ── process_once ───────────────────────────────────────────

class TestProcessOnce:
    """Tests for process_once()."""

    @patch("ml_client.save_result", return_value="inserted_id")
    @patch("ml_client.run_inference", return_value=[{"class": "PAPER"}])
    @patch("ml_client.capture_image", return_value="capture.jpg")
    def test_full_cycle(self, _cap, _infer, _save):
        """Should complete full capture → infer → save cycle."""
        mock_col = MagicMock()
        result = process_once(mock_col)
        assert result == "inserted_id"

    @patch("ml_client.capture_image", return_value=None)
    def test_skips_if_no_image(self, _cap):
        """Should return None and skip if capture fails."""
        mock_col = MagicMock()
        result = process_once(mock_col)
        assert result is None