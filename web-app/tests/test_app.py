import pytest
from app import create_app


@pytest.fixture
def client():
    """
    Create and yield Flask app
    """
    app = create_app()
    app.testing = True  # necessary for assertions to work correctly
    with app.test_client() as client:
        yield client
