import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app import app
def test_app_exists():
    assert app is not None

def test_home_route():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200

def test_home_page_content():
    client = app.test_client()
    response = client.get("/")
    data = response.get_data(as_text=True)
    
    assert len(data) > 0