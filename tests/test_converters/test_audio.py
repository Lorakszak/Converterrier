import subprocess
import pytest

from converterrier.converters.audio import AudioConverter


@pytest.fixture
def converter():
    return AudioConverter()


@pytest.fixture
def wav_file(tmp_path):
    path = tmp_path / "test.wav"
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "sine=frequency=440:duration=1",
            "-ac", "1", str(path),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip("FFmpeg not available")
    return path


def test_category(converter):
    assert converter.category == "audio"


def test_supported_formats_has_mp3(converter):
    formats = converter.get_supported_formats()
    assert "wav" in formats
    assert "mp3" in formats["wav"]


def test_settings_schema_has_bitrate(converter):
    schema = converter.get_settings_schema("wav")
    assert "bitrate" in schema
    assert schema["bitrate"]["type"] == "select"


def test_convert_wav_to_mp3(converter, wav_file):
    output = converter.convert(wav_file, "mp3", {})
    assert output.exists()
    assert output.suffix == ".mp3"
    assert output.stat().st_size > 0


def test_convert_with_bitrate(converter, wav_file):
    output = converter.convert(wav_file, "ogg", {"bitrate": "128k"})
    assert output.exists()
    assert output.suffix == ".ogg"


def test_convert_with_mono(converter, wav_file):
    output = converter.convert(wav_file, "mp3", {"channels": "mono"})
    assert output.exists()
