from io import BytesIO
from unittest.mock import patch


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Fridge Food Detector" in response.data


def test_dashboard_page(client):
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Inventory Dashboard" in response.data


def test_upload_route_success(client):
    with patch("routes.run_ml_detection") as mock_run_ml_detection, patch(
        "routes.save_detection_results_to_db"
    ) as mock_save_detection_results:
        mock_run_ml_detection.return_value = (
            "fake_task",
            "fake_output_dir",
            "fake_json_path",
        )

        data = {
            "image": (BytesIO(b"fake image data"), "fridge.png"),
        }

        response = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=False,
        )

        assert response.status_code == 302
        mock_run_ml_detection.assert_called_once()
        mock_save_detection_results.assert_called_once()


def test_upload_route_missing_file(client):
    response = client.post(
        "/upload",
        data={},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert b"No file part in request" in response.data


def test_upload_route_empty_filename(client):
    data = {
        "image": (BytesIO(b""), ""),
    }

    response = client.post(
        "/upload",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"No selected file" in response.data


def test_upload_route_invalid_extension(client):
    data = {
        "image": (BytesIO(b"fake data"), "bad.txt"),
    }

    response = client.post(
        "/upload",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert b"Unsupported file type" in response.data


def test_edit_item_route(client):
    with patch("routes.update_inventory_item_name") as mock_update:
        response = client.post(
            "/items/1234567890abcdef12345678/edit",
            data={"display_name": "green cucumber"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        mock_update.assert_called_once_with(
            "1234567890abcdef12345678", "green cucumber"
        )


def test_delete_item_route(client):
    with patch("routes.soft_delete_inventory_item") as mock_delete:
        response = client.post(
            "/items/1234567890abcdef12345678/delete",
            follow_redirects=False,
        )

        assert response.status_code == 302
        mock_delete.assert_called_once_with("1234567890abcdef12345678")
