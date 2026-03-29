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


def test_settings_schema_quality_has_formats(converter):
    schema = converter.get_settings_schema("mp4")
    assert "formats" in schema["quality"]
    assert "mp4" in schema["quality"]["formats"]
    assert "gif" not in schema["quality"]["formats"]


def test_settings_schema_has_preset(converter):
    schema = converter.get_settings_schema("mp4")
    assert "preset" in schema
    assert schema["preset"]["advanced"] is True
    assert schema["preset"]["type"] == "select"
    assert "mp4" in schema["preset"]["formats"]
    assert "gif" not in schema["preset"]["formats"]


def test_settings_schema_has_tune(converter):
    schema = converter.get_settings_schema("mp4")
    assert "tune" in schema
    assert schema["tune"]["advanced"] is True
    assert "mp4" in schema["tune"]["formats"]


def test_settings_schema_has_fps(converter):
    schema = converter.get_settings_schema("mp4")
    assert "fps" in schema
    assert schema["fps"]["advanced"] is True
    assert schema["fps"]["type"] == "select"


def test_settings_schema_has_strip_audio(converter):
    schema = converter.get_settings_schema("mp4")
    assert "strip_audio" in schema
    assert schema["strip_audio"]["advanced"] is True
    assert schema["strip_audio"]["type"] == "checkbox"


def test_settings_schema_has_gif_fps(converter):
    schema = converter.get_settings_schema("mp4")
    assert "gif_fps" in schema
    assert schema["gif_fps"]["advanced"] is True
    assert "gif" in schema["gif_fps"]["formats"]


def test_settings_schema_has_gif_width(converter):
    schema = converter.get_settings_schema("mp4")
    assert "gif_width" in schema
    assert schema["gif_width"]["advanced"] is True
    assert "gif" in schema["gif_width"]["formats"]


def test_convert_mp4_to_webm(converter, mp4_file):
    output = converter.convert(mp4_file, "webm", {})
    assert output.exists()
    assert output.suffix == ".webm"
    assert output.stat().st_size > 0


def test_convert_with_resolution(converter, mp4_file):
    output = converter.convert(mp4_file, "mkv", {"resolution": "720p"})
    assert output.exists()
    assert output.suffix == ".mkv"


def test_convert_with_preset(converter, mp4_file):
    output = converter.convert(mp4_file, "mkv", {"preset": "ultrafast"})
    assert output.exists()
    assert output.stat().st_size > 0


def test_convert_with_tune(converter, mp4_file):
    output = converter.convert(mp4_file, "mkv", {"tune": "animation"})
    assert output.exists()
    assert output.stat().st_size > 0


def test_convert_with_fps(converter, mp4_file):
    output = converter.convert(mp4_file, "mkv", {"fps": "24"})
    assert output.exists()
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate",
         "-of", "csv=p=0", str(output)],
        capture_output=True, text=True,
    )
    assert "24" in result.stdout.strip()


def test_convert_with_strip_audio(converter, mp4_file):
    output = converter.convert(mp4_file, "mkv", {"strip_audio": True})
    assert output.exists()
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=codec_type",
         "-of", "csv=p=0", str(output)],
        capture_output=True, text=True,
    )
    assert result.stdout.strip() == ""


def test_convert_to_gif(converter, mp4_file):
    output = converter.convert(mp4_file, "gif", {})
    assert output.exists()
    assert output.suffix == ".gif"


def test_convert_to_gif_custom_fps(converter, mp4_file):
    output = converter.convert(mp4_file, "gif", {"gif_fps": "5"})
    assert output.exists()
    assert output.suffix == ".gif"


def test_convert_to_gif_custom_width(converter, mp4_file):
    output = converter.convert(mp4_file, "gif", {"gif_width": "320"})
    assert output.exists()
    assert output.suffix == ".gif"


def test_convert_to_gif_original_width(converter, mp4_file):
    output = converter.convert(mp4_file, "gif", {"gif_width": "original"})
    assert output.exists()
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width",
         "-of", "csv=p=0", str(output)],
        capture_output=True, text=True,
    )
    assert result.stdout.strip() == "320"
