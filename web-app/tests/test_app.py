"""Tests for the web application."""

# pylint: disable=redefined-outer-name
import datetime

import pytest
from bson.objectid import ObjectId

from app import app  # pylint: disable=import-error
from db import speeches_collection, users_collection  # pylint: disable=import-error


@pytest.fixture
def client():
    """Set up Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_login_page(client):
    """Test that the login page loads."""
    response = client.get("/login")
    assert response.status_code == 200


def test_index_redirects_not_loggedin(client):
    """Test that index redirects if not logged in."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location


def test_index_loggedin(client):
    """Test index redirects to dashboard when correctly logged in."""
    client.post(
        "/signup",
        data={
            "username": "testindex",
            "password": "password123",
            "password2": "password123",
        },
    )
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200


def test_dashboard_not_loggedin(client):
    """Test that dashboard redirects to login if not logged in."""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location


def test_record_not_loggedin(client):
    """Test that record page redirects to login if not logged in."""
    response = client.get("/record")
    assert response.status_code == 302
    assert "/login" in response.location


def test_submit_not_loggedin(client):
    """Test that submitting redirects to login if not logged in."""
    response = client.post("/submit")
    assert response.status_code == 302
    assert "/login" in response.location


def test_logout_tologin(client):
    """Test that pressing logout redirects to login."""
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.location


def test_signup_page(client):
    """Test that the signup page loads."""
    response = client.get("/signup")
    assert response.status_code == 200


def test_loggedin_signup(client):
    """Test signup redirects to dashboard if already logged in."""
    client.post(
        "/signup",
        data={
            "username": "alreadysigned",
            "password": "password123",
            "password2": "password123",
        },
    )
    response = client.get("/signup", follow_redirects=True)
    assert response.status_code == 200


def test_emptylogin_username(client):
    """Test login with empty username shows error."""
    response = client.post("/login", data={"username": "", "password": "Testing"})
    assert response.status_code == 200
    assert b"Enter a username and password." in response.data


def test_wrong_login(client):
    """Test login with incorrect username shows error."""
    response = client.post(
        "/login", data={"username": "fakeuser1234", "password": "wrongpassword"}
    )
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data


def test_login_wrong_password(client):
    """Test login with correct username but wrong password shows error."""
    client.post(
        "/signup",
        data={
            "username": "wronguser",
            "password": "correctpassword",
            "password2": "correctpassword",
        },
    )
    client.get("/logout")
    response = client.post(
        "/login", data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_successful_login(client):
    """Test successful login redirects to dashboard."""
    client.post(
        "/signup",
        data={
            "username": "successlogin",
            "password": "password123",
            "password2": "password123",
        },
    )
    client.get("/logout")
    response = client.post(
        "/login",
        data={
            "username": "successlogin", 
            "password": 
            "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Your Speech Dashboard" in response.data


def test_emptylogin_password(client):
    """Test login with an empty password"""
    response = client.post("/login", data={"username": "ronweasley", "password": ""})
    assert response.status_code == 200
    assert b"Enter a username and password." in response.data


def test_emptysignup_username(client):
    """Test signup with empty username shows error."""
    response = client.post(
        "/signup",
        data={"username": "", "password": "password123", "password2": "password123"},
    )
    assert response.status_code == 200
    assert b"Please enter a username and password." in response.data


def test_emptysignup_password(client):
    """Test signup with empty password shows error."""
    response = client.post(
        "/signup", data={"username": "testuser", "password": "", "password2": ""}
    )
    assert response.status_code == 200
    assert b"Please enter a username and password." in response.data


def test_signup_passmatch(client):
    """Test signup with non matching passwords shows error message."""
    response = client.post(
        "/signup",
        data={
            "username": "testinguser",
            "password": "password1",
            "password2": "password2",
        },
    )
    assert response.status_code == 200
    assert b"Passwords do not match." in response.data


def test_signup_taken_username(client):
    """Test signup with a taken username shows error."""
    client.post(
        "/signup",
        data={
            "username": "sameuser",
            "password": "password123",
            "password2": "password123",
        },
    )
    client.get("/logout")
    response = client.post(
        "/signup",
        data={
            "username": "sameuser",
            "password": "password1234",
            "password2": "password1234",
        },
    )
    assert response.status_code == 200
    assert b"Username already taken." in response.data


def test_submit_no_title(client):
    """Test submitting with no title redirects back to record."""
    client.post(
        "/signup",
        data={
            "username": "testinguser123",
            "password": "password123",
            "password2": "password123",
        },
    )
    response = client.post(
        "/submit",
        data={
            "title": "",
        },
    )
    assert response.status_code == 302
    assert "/record" in response.location


def test_submit_no_audio(client):
    """Test submitting with no audio file redirects back to record."""
    client.post(
        "/signup",
        data={
            "username": "testinguser1234",
            "password": "password123",
            "password2": "password123",
        },
    )
    response = client.post(
        "/submit",
        data={
            "title": "My speech",
        },
    )
    assert response.status_code == 302
    assert "/record" in response.location


def test_delete_speech(client):
    """Test that deleting a speech removes it from the database."""
    client.post(
        "/signup",
        data={
            "username": "deletetest",
            "password": "password123",
            "password2": "password123",
        },
    )
    user = users_collection.find_one({"username": "deletetest"})
    user_id = str(user["_id"])
    result = speeches_collection.insert_one(
        {
            "user_id": user_id,
            "title": "Speech to delete",
            "timestamp": datetime.datetime.utcnow(),
        }
    )
    speech_id = str(result.inserted_id)
    response = client.post(f"/delete/{speech_id}", follow_redirects=True)  # ✅ store it
    assert response.status_code == 200
    deleted = speeches_collection.find_one({"_id": ObjectId(speech_id)})
    assert deleted is None


def test_invalid_delete(client):
    """Test delete with invalid speech id shows error."""
    client.post(
        "/signup",
        data={
            "username": "invaliddelete",
            "password": "password123",
            "password2": "password123",
        },
    )
    response = client.post("/delete/notavalidid", follow_redirects=True)
    assert response.status_code == 200
