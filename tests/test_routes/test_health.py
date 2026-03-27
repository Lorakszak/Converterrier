from fastapi.testclient import TestClient

from converterrier.app import create_app


def test_health_returns_status():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ffmpeg" in data
    assert "pandoc" in data
    assert "pandoc_pdf" in data
