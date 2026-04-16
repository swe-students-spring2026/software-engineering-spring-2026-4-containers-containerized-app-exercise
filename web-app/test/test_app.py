"""Unit tests for Flask web app routes."""

# pylint: disable=missing-class-docstring,missing-function-docstring,too-few-public-methods,unused-argument

import pytest
from bson import ObjectId

import app as web_app
from app import app as flask_app


@pytest.fixture(name="client")
def fixture_client():
    """Create a test client for the Flask app."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


def test_guide_page_status(client):
    """Test if the guide page returns a 200 status code."""
    res = client.get("/guide")
    assert res.status_code == 200
    assert b"Garbage Classification Guide" in res.data


def test_guide_content_categories(client):
    """Test if the guide page contains the 4 main garbage categories."""
    res = client.get("/guide")
    html_content = res.data.decode("utf-8")

    assert "Recyclable" in html_content
    assert "Hazardous" in html_content
    assert "Food / Kitchen" in html_content
    assert "Other / General" in html_content


def test_unknown_route_returns_404(client):
    """Test that an unknown route correctly returns a 404 status."""
    res = client.get("/nonexistent")
    assert res.status_code == 404


def test_normalize_confidence_decimal():
    """Confidence decimal values should become integer percentages."""
    assert web_app.normalize_confidence(0.91) == 91


def test_normalize_confidence_percent_string():
    """Confidence strings with percent signs should be normalized."""
    assert web_app.normalize_confidence("92%") == 92


def test_normalize_confidence_invalid():
    """Invalid confidence values should fall back to 0."""
    assert web_app.normalize_confidence("abc") == 0


def test_map_bin_blue():
    """Recyclable material categories should map to the blue bin."""
    assert web_app.map_bin("PLASTIC") == "Blue"
    assert web_app.map_bin("glass") == "Blue"
    assert web_app.map_bin("CARDBOARD") == "Blue"


def test_map_bin_green():
    """Biodegradable material categories should map to the green bin."""
    assert web_app.map_bin("BIODEGRADABLE") == "Green"
    assert web_app.map_bin("food waste") == "Green"


def test_map_bin_gray():
    """Trash-like categories should map to the gray bin."""
    assert web_app.map_bin("cloth") == "Gray"
    assert web_app.map_bin("landfill") == "Gray"


def test_map_bin_unknown():
    """Unknown categories should map to Unknown."""
    assert web_app.map_bin("randomthing") == "Unknown"
    assert web_app.map_bin(None) == "Unknown"


def test_get_bin_color():
    """Bin colors should map to the expected hex codes."""
    assert web_app.get_bin_color("Blue") == "#2196F3"
    assert web_app.get_bin_color("Green") == "#2e8b57"
    assert web_app.get_bin_color("Gray") == "#666666"
    assert web_app.get_bin_color("SomethingElse") == "#999999"


def test_get_bin_emoji():
    """Bins should map to the expected emoji."""
    assert web_app.get_bin_emoji("Blue") == "♻️"
    assert web_app.get_bin_emoji("Green") == "🌱"
    assert web_app.get_bin_emoji("Gray") == "🗑️"
    assert web_app.get_bin_emoji("SomethingElse") == "❓"


def test_build_dashboard_stats():
    """Dashboard stats should summarize records correctly."""
    records = [
        {"category": "PLASTIC", "bin": "Blue"},
        {"category": "PLASTIC", "bin": "Blue"},
        {"category": "BIODEGRADABLE", "bin": "Green"},
        {"category": "CLOTH", "bin": "Gray"},
    ]

    stats = web_app.build_dashboard_stats(records)

    assert stats["total_records"] == 4
    assert stats["blue_bin"] == 2
    assert stats["green_bin"] == 1
    assert stats["gray_bin"] == 1
    assert stats["unknown_bin"] == 0
    assert stats["top_category"] == "PLASTIC"


def test_format_record_for_display():
    """Formatting a record should add display-only values."""
    record = {
        "_id": ObjectId(),
        "item": "bottle",
        "category": "PLASTIC",
        "bin": "Blue",
        "confidence": 88,
        "timestamp": "2026-04-16 04:00:00",
    }

    formatted = web_app.format_record_for_display(record)

    assert isinstance(formatted["_id"], str)
    assert formatted["bin_color"] == "#2196F3"
    assert formatted["bin_emoji"] == "♻️"
    assert formatted["item"] == "bottle"
    assert formatted["category"] == "PLASTIC"


def test_index_route_status(client, monkeypatch):
    """Home page should render successfully."""
    fake_records = [
        {
            "_id": ObjectId(),
            "item": "bottle",
            "category": "PLASTIC",
            "bin": "Blue",
            "confidence": 88,
            "timestamp": "2026-04-16 04:00:00",
        }
    ]

    class FakeCursor:
        def sort(self, *args, **kwargs):
            return self

        def limit(self, *args, **kwargs):
            return fake_records

    class FakeCollection:
        def find(self, *args, **kwargs):
            return FakeCursor()

    monkeypatch.setattr(web_app, "collection", FakeCollection())

    res = client.get("/")
    assert res.status_code == 200
    assert b"Smart Garbage Classifier" in res.data
    assert b"Total Classifications" in res.data


def test_history_route_status(client, monkeypatch):
    """History page should render successfully."""
    fake_records = [
        {
            "_id": ObjectId(),
            "item": "paper",
            "category": "PAPER",
            "bin": "Blue",
            "confidence": 72,
            "timestamp": "2026-04-16 04:05:00",
        }
    ]

    class FakeCursor:
        def sort(self, *args, **kwargs):
            return self

        def limit(self, *args, **kwargs):
            return fake_records

    class FakeCollection:
        def find(self, *args, **kwargs):
            return FakeCursor()

    monkeypatch.setattr(web_app, "collection", FakeCollection())

    res = client.get("/history")
    assert res.status_code == 200
    assert b"Recognition History" in res.data
    assert b"PAPER" in res.data


def test_result_detail_not_found(client, monkeypatch):
    """Unknown result ids should return 404."""

    class FakeCollection:
        def find_one(self, *args, **kwargs):
            return None

    monkeypatch.setattr(web_app, "collection", FakeCollection())

    res = client.get(f"/result/{ObjectId()}")
    assert res.status_code == 404
    assert b"Record not found" in res.data


def test_result_detail_found(client, monkeypatch):
    """A valid result record should render the detail page."""
    fake_record = {
        "_id": ObjectId(),
        "item": "bottle",
        "category": "PLASTIC",
        "bin": "Blue",
        "confidence": 95,
        "timestamp": "2026-04-16 04:00:00",
    }

    class FakeCollection:
        def find_one(self, *args, **kwargs):
            return fake_record

    monkeypatch.setattr(web_app, "collection", FakeCollection())

    res = client.get(f"/result/{ObjectId()}")
    assert res.status_code == 200
    assert b"Classification Result" in res.data
    assert b"PLASTIC" in res.data


def test_build_result_defaults():
    """build_result should create the expected default result structure."""
    result = web_app.build_result("banana peel")

    assert result["item"] == "banana peel"
    assert result["category"] == "Unknown"
    assert result["bin"] == "Unknown"
    assert result["confidence"] == 0
    assert result["model_error"] is None
    assert "timestamp" in result


def test_normalize_json_objectid():
    """normalize_json should convert ObjectId values to strings recursively."""
    oid = ObjectId()
    payload = {
        "_id": oid,
        "nested": {"value": oid},
        "items": [oid],
    }

    normalized = web_app.normalize_json(payload)

    assert normalized["_id"] == str(oid)
    assert normalized["nested"]["value"] == str(oid)
    assert normalized["items"][0] == str(oid)


def test_extract_prediction_with_predictions():
    """extract_prediction should use the first prediction from the model response."""
    result = web_app.build_result("bottle")
    response_data = {"predictions": [{"class": "PLASTIC", "confidence": 0.87}]}

    web_app.extract_prediction(response_data, result)

    assert result["category"] == "PLASTIC"
    assert result["confidence"] == 87
    assert result["bin"] == "Blue"


def test_extract_prediction_without_predictions():
    """extract_prediction should fall back to top-level category/confidence fields."""
    result = web_app.build_result("scrap")
    response_data = {"category": "METAL", "confidence": "91%"}

    web_app.extract_prediction(response_data, result)

    assert result["category"] == "METAL"
    assert result["confidence"] == 91
    assert result["bin"] == "Blue"
