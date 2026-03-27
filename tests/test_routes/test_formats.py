from fastapi.testclient import TestClient

from converterrier.app import create_app


def test_formats_returns_all_categories():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/formats")
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
    assert "audio" in data
    assert "video" in data
    assert "document" in data


def test_formats_image_has_targets():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/formats")
    data = response.json()
    png = data["image"]["png"]
    assert "targets" in png
    assert "jpg" in png["targets"]
    assert "settings" in png
