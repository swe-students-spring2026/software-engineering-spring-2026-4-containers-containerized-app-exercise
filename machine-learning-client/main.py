"""Execution entry point for realtime inference."""

from src.server import app


def analyze_posture():
    """Placeholder function kept for compatibility with existing tests."""
    return True


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
