import pytest

from app.app import create_app


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        ML_CLIENT_URL="http://localhost:5001",
    )
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()