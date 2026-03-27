import io
import zipfile

from PIL import Image
from fastapi.testclient import TestClient

from converterrier.app import create_app


def _make_png_bytes() -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def test_convert_png_to_jpg():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.png", _make_png_bytes(), "image/png")},
        data={"target_format": "jpg"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert "test.jpg" in response.headers["content-disposition"]
    img = Image.open(io.BytesIO(response.content))
    assert img.format == "JPEG"


def test_convert_with_settings():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.png", _make_png_bytes(), "image/png")},
        data={"target_format": "webp", "settings": '{"quality": 50}'},
    )
    assert response.status_code == 200


def test_convert_unsupported_format():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.xyz", b"not a real file", "application/octet-stream")},
        data={"target_format": "jpg"},
    )
    assert response.status_code == 400


def test_convert_unsupported_target():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.png", _make_png_bytes(), "image/png")},
        data={"target_format": "mp3"},
    )
    assert response.status_code == 400


def test_convert_file_too_large():
    app = create_app(max_size=10)
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.png", _make_png_bytes(), "image/png")},
        data={"target_format": "jpg"},
    )
    assert response.status_code == 413


def test_batch_convert():
    app = create_app()
    client = TestClient(app)
    png1 = _make_png_bytes()
    png2 = _make_png_bytes()
    response = client.post(
        "/api/convert/batch",
        files=[
            ("files", ("img1.png", png1, "image/png")),
            ("files", ("img2.png", png2, "image/png")),
        ],
        data={"target_format": "jpg"},
    )
    assert response.status_code == 200
    assert "application/zip" in response.headers["content-type"]

    z = zipfile.ZipFile(io.BytesIO(response.content))
    names = z.namelist()
    assert len(names) == 2
    assert "img1.jpg" in names
    assert "img2.jpg" in names
