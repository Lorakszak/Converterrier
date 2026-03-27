import subprocess
import pytest

from converterrier.converters.video import VideoConverter


@pytest.fixture
def converter():
    return VideoConverter()


@pytest.fixture
def mp4_file(tmp_path):
    path = tmp_path / "test.mp4"
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=1:size=320x240:rate=1",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
            "-c:v", "libx264", "-c:a", "aac", "-shortest",
            str(path),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip("FFmpeg not available or missing codecs")
    return path


def test_category(converter):
    assert converter.category == "video"


def test_supported_formats_has_mp4(converter):
    formats = converter.get_supported_formats()
    assert "mp4" in formats
    assert "webm" in formats["mp4"]


def test_settings_schema_has_resolution(converter):
    schema = converter.get_settings_schema("mp4")
    assert "resolution" in schema
    assert "quality" in schema


def test_convert_mp4_to_webm(converter, mp4_file):
    output = converter.convert(mp4_file, "webm", {})
    assert output.exists()
    assert output.suffix == ".webm"
    assert output.stat().st_size > 0


def test_convert_with_resolution(converter, mp4_file):
    output = converter.convert(mp4_file, "mkv", {"resolution": "720p"})
    assert output.exists()
    assert output.suffix == ".mkv"


def test_convert_to_gif(converter, mp4_file):
    output = converter.convert(mp4_file, "gif", {})
    assert output.exists()
    assert output.suffix == ".gif"
