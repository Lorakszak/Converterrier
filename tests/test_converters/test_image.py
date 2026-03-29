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


def test_settings_schema_has_advanced_jpeg_params(converter):
    schema = converter.get_settings_schema("png")
    assert "progressive" in schema
    assert schema["progressive"]["advanced"] is True
    assert schema["progressive"]["type"] == "checkbox"
    assert "jpg" in schema["progressive"]["formats"]
    assert "png" not in schema["progressive"]["formats"]


def test_settings_schema_has_advanced_png_params(converter):
    schema = converter.get_settings_schema("png")
    assert "compress_level" in schema
    assert schema["compress_level"]["advanced"] is True
    assert schema["compress_level"]["type"] == "range"
    assert "png" in schema["compress_level"]["formats"]


def test_settings_schema_has_advanced_webp_params(converter):
    schema = converter.get_settings_schema("png")
    assert "lossless" in schema
    assert schema["lossless"]["advanced"] is True
    assert schema["lossless"]["type"] == "checkbox"
    assert "webp" in schema["lossless"]["formats"]


def test_settings_schema_has_advanced_tiff_params(converter):
    schema = converter.get_settings_schema("png")
    assert "compression" in schema
    assert schema["compression"]["advanced"] is True
    assert schema["compression"]["type"] == "select"
    assert "tiff" in schema["compression"]["formats"]


def test_settings_schema_has_advanced_gif_params(converter):
    schema = converter.get_settings_schema("png")
    assert "optimize" in schema
    assert schema["optimize"]["advanced"] is True
    assert "gif" in schema["optimize"]["formats"]


def test_convert_jpg_progressive(converter, png_file):
    output = converter.convert(png_file, "jpg", {"progressive": True})
    assert output.exists()
    img = Image.open(output)
    assert img.info.get("progressive") or img.info.get("progression")


def test_convert_jpg_optimize(converter, png_file):
    output_normal = converter.convert(png_file, "jpg", {"quality": 85})
    size_normal = output_normal.stat().st_size
    output_opt = converter.convert(png_file, "jpg", {"quality": 85, "optimize": True})
    size_opt = output_opt.stat().st_size
    assert size_opt <= size_normal


def test_convert_jpg_subsampling(converter, png_file):
    output = converter.convert(png_file, "jpg", {"subsampling": "4:4:4"})
    assert output.exists()
    img = Image.open(output)
    assert img.format == "JPEG"


def test_convert_png_compress_level(converter, png_file):
    output_0 = converter.convert(png_file, "png", {"compress_level": 0})
    size_0 = output_0.stat().st_size
    output_9 = converter.convert(png_file, "png", {"compress_level": 9})
    size_9 = output_9.stat().st_size
    assert size_9 <= size_0


def test_convert_webp_lossless(converter, png_file):
    output = converter.convert(png_file, "webp", {"lossless": True})
    assert output.exists()
    assert output.suffix == ".webp"


def test_convert_webp_method(converter, png_file):
    output = converter.convert(png_file, "webp", {"method": 6})
    assert output.exists()
    assert output.suffix == ".webp"


def test_convert_tiff_compression(converter, png_file):
    output = converter.convert(png_file, "tiff", {"compression": "tiff_lzw"})
    assert output.exists()
    img = Image.open(output)
    assert img.format == "TIFF"


def test_convert_gif_interlace(converter, png_file):
    output = converter.convert(png_file, "gif", {"interlace": True})
    assert output.exists()
    img = Image.open(output)
    assert img.format == "GIF"


def test_convert_to_ico(converter, tmp_path):
    path = tmp_path / "large.png"
    img = Image.new("RGBA", (512, 512), color=(0, 255, 0, 255))
    img.save(path, format="PNG")
    output = converter.convert(path, "ico", {})
    assert output.exists()
    assert output.suffix == ".ico"
