"""Tests for the worker module."""

from app import worker


def test_process_next_scan_returns_false_when_no_scan(monkeypatch):
    """Worker should return False when no work is available."""
    monkeypatch.setattr(worker, "get_next_pending_scan", lambda: None)
    assert worker.process_next_scan() is False


def test_process_next_scan_success(monkeypatch):
    """Worker should process a valid pending scan."""
    recorded = {}

    monkeypatch.setattr(
        worker,
        "get_next_pending_scan",
        lambda: {
            "_id": "scan-1",
            "image_path": "uploads/test.jpg",
            "target_emotion": "happy",
        },
    )
    monkeypatch.setattr(worker.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(
        worker,
        "analyze_image",
        lambda image_path, target_emotion: {
            "predicted_emotion": "happy",
            "emotion_scores": {"happy": 95.0},
            "match_score": 95.0,
            "passed": True,
            "face_detected": True,
            "processing_time_ms": 10,
        },
    )

    def fake_mark_done(scan_id, result):
        recorded["scan_id"] = scan_id
        recorded["result"] = result

    monkeypatch.setattr(worker, "mark_scan_done", fake_mark_done)
    monkeypatch.setattr(
        worker, "mark_scan_error", lambda *_args: recorded.update({"error": True})
    )

    processed = worker.process_next_scan()

    assert processed is True
    assert recorded["scan_id"] == "scan-1"
    assert recorded["result"]["predicted_emotion"] == "happy"
    assert "error" not in recorded


def test_process_next_scan_marks_error_when_file_missing(monkeypatch):
    """Worker should mark a scan as error when the image file is missing."""
    recorded = {}

    monkeypatch.setattr(
        worker,
        "get_next_pending_scan",
        lambda: {
            "_id": "scan-2",
            "image_path": "uploads/missing.jpg",
            "target_emotion": "sad",
        },
    )
    monkeypatch.setattr(worker.os.path, "exists", lambda _path: False)
    monkeypatch.setattr(
        worker, "mark_scan_done", lambda *_args: recorded.update({"done": True})
    )

    def fake_mark_error(scan_id, message):
        recorded["scan_id"] = scan_id
        recorded["message"] = message

    monkeypatch.setattr(worker, "mark_scan_error", fake_mark_error)

    processed = worker.process_next_scan()

    assert processed is True
    assert recorded["scan_id"] == "scan-2"
    assert "Image not found" in recorded["message"]
    assert "done" not in recorded
