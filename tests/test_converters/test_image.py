import pytest
from PIL import Image

from converterrier.converters.image import ImageConverter


@pytest.fixture
def converter():
    return ImageConverter()


@pytest.fixture
def png_file(tmp_path):
    path = tmp_path / "test.png"
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
    img.save(path, format="PNG")
    return path


def test_category(converter):
    assert converter.category == "image"


def test_supported_formats_has_png(converter):
    formats = converter.get_supported_formats()
    assert "png" in formats
    assert "jpg" in formats["png"]


def test_settings_schema_has_quality(converter):
    schema = converter.get_settings_schema("png")
    assert "quality" in schema
    assert schema["quality"]["type"] == "range"


def test_convert_png_to_jpg(converter, png_file):
    output = converter.convert(png_file, "jpg", {})
    assert output.exists()
    assert output.suffix == ".jpg"
    img = Image.open(output)
    assert img.format == "JPEG"


def test_convert_with_quality(converter, png_file):
    output = converter.convert(png_file, "webp", {"quality": 50})
    assert output.exists()
    assert output.suffix == ".webp"


def test_convert_with_resize(converter, png_file):
    output = converter.convert(png_file, "jpg", {"resize_width": 50, "resize_height": 50})
    assert output.exists()
    img = Image.open(output)
    assert img.size == (50, 50)


def test_convert_rgba_to_jpg_strips_alpha(converter, png_file):
    output = converter.convert(png_file, "jpg", {})
    img = Image.open(output)
    assert img.mode == "RGB"


def test_convert_to_ico(converter, tmp_path):
    path = tmp_path / "large.png"
    img = Image.new("RGBA", (512, 512), color=(0, 255, 0, 255))
    img.save(path, format="PNG")
    output = converter.convert(path, "ico", {})
    assert output.exists()
    assert output.suffix == ".ico"
