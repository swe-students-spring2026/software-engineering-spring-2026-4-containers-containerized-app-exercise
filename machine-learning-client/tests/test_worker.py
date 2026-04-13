"""Tests for the worker module."""

import pytest

from app import worker as worker_module


def test_run_worker_processes_scan_successfully(monkeypatch):
    """Worker should process a valid scan and store the result."""
    scan = {"_id": "scan-1", "image_path": "sample_data/test.jpg"}
    stored = {}

    monkeypatch.setattr(worker_module, "get_next_pending_scan", lambda: scan)
    monkeypatch.setattr(worker_module.os.path, "exists", lambda path: True)
    monkeypatch.setattr(
        worker_module,
        "analyze_image",
        lambda path: {
            "dominant_emotion": "happy",
            "emotion_scores": {"happy": 90.0},
            "face_detected": True,
            "processing_time_ms": 10,
        },
    )

    def fake_mark_scan_done(scan_id, result):
        stored["scan_id"] = scan_id
        stored["result"] = result
        raise SystemExit

    monkeypatch.setattr(worker_module, "mark_scan_done", fake_mark_scan_done)
    monkeypatch.setattr(worker_module, "mark_scan_error", lambda *_args: None)

    with pytest.raises(SystemExit):
        worker_module.run_worker()

    assert stored["scan_id"] == "scan-1"
    assert stored["result"]["dominant_emotion"] == "happy"


def test_run_worker_marks_error_when_file_missing(monkeypatch):
    """Worker should mark the scan as failed if the image file is missing."""
    scan = {"_id": "scan-2", "image_path": "missing.jpg"}
    stored = {}

    monkeypatch.setattr(worker_module, "get_next_pending_scan", lambda: scan)
    monkeypatch.setattr(worker_module.os.path, "exists", lambda path: False)
    monkeypatch.setattr(
        worker_module,
        "analyze_image",
        lambda path: {
            "dominant_emotion": "happy",
            "emotion_scores": {"happy": 90.0},
            "face_detected": True,
            "processing_time_ms": 10,
        },
    )
    monkeypatch.setattr(worker_module, "mark_scan_done", lambda *_args: None)

    def fake_mark_scan_error(scan_id, message):
        stored["scan_id"] = scan_id
        stored["message"] = message
        raise SystemExit

    monkeypatch.setattr(worker_module, "mark_scan_error", fake_mark_scan_error)

    with pytest.raises(SystemExit):
        worker_module.run_worker()

    assert stored["scan_id"] == "scan-2"
    assert "Image not found" in stored["message"]


def test_run_worker_sleeps_when_no_pending_scan(monkeypatch):
    """Worker should sleep if there are no pending scans."""
    monkeypatch.setattr(worker_module, "get_next_pending_scan", lambda: None)

    def fake_sleep(_seconds):
        raise SystemExit

    monkeypatch.setattr(worker_module.time, "sleep", fake_sleep)

    with pytest.raises(SystemExit):
        worker_module.run_worker()
