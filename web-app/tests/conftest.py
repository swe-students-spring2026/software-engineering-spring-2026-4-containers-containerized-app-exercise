import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app


@pytest.fixture
def app():
    temp_upload_dir = tempfile.mkdtemp()
    temp_runtime_dir = tempfile.mkdtemp()

    app = create_app(
        {
            "TESTING": True,
            "UPLOAD_FOLDER": temp_upload_dir,
            "RUNTIME_FOLDER": temp_runtime_dir,
        }
    )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()