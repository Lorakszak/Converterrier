from converterrier.converters import get_converter_for_format, get_all_formats


def test_get_converter_for_png():
    converter = get_converter_for_format("png")
    assert converter is not None
    assert converter.category == "image"


def test_get_converter_for_mp3():
    converter = get_converter_for_format("mp3")
    assert converter is not None
    assert converter.category == "audio"


def test_get_converter_for_mp4():
    converter = get_converter_for_format("mp4")
    assert converter is not None
    assert converter.category == "video"


def test_get_converter_for_md():
    converter = get_converter_for_format("md")
    assert converter is not None
    assert converter.category == "document"


def test_get_converter_for_unknown():
    converter = get_converter_for_format("xyz123")
    assert converter is None


def test_get_all_formats_has_categories():
    formats = get_all_formats()
    assert "image" in formats
    assert "audio" in formats
    assert "video" in formats
    assert "document" in formats
    assert "png" in formats["image"]
