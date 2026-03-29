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


def test_settings_schema_bitrate_has_formats(converter):
    schema = converter.get_settings_schema("wav")
    assert "formats" in schema["bitrate"]
    assert "mp3" in schema["bitrate"]["formats"]
    assert "wav" not in schema["bitrate"]["formats"]
    assert "flac" not in schema["bitrate"]["formats"]


def test_settings_schema_has_sample_rate(converter):
    schema = converter.get_settings_schema("wav")
    assert "sample_rate" in schema
    assert schema["sample_rate"]["advanced"] is True
    assert schema["sample_rate"]["type"] == "select"


def test_settings_schema_has_flac_compression(converter):
    schema = converter.get_settings_schema("wav")
    assert "compression_level" in schema
    assert schema["compression_level"]["advanced"] is True
    assert schema["compression_level"]["type"] == "range"
    assert "flac" in schema["compression_level"]["formats"]


def test_settings_schema_has_wav_bit_depth(converter):
    schema = converter.get_settings_schema("wav")
    assert "bit_depth" in schema
    assert schema["bit_depth"]["advanced"] is True
    assert schema["bit_depth"]["type"] == "select"
    assert "wav" in schema["bit_depth"]["formats"]


def test_settings_schema_has_normalize(converter):
    schema = converter.get_settings_schema("wav")
    assert "normalize" in schema
    assert schema["normalize"]["advanced"] is True
    assert schema["normalize"]["type"] == "checkbox"


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


def test_convert_with_sample_rate(converter, wav_file):
    output = converter.convert(wav_file, "mp3", {"sample_rate": "22050"})
    assert output.exists()
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=sample_rate",
         "-of", "csv=p=0", str(output)],
        capture_output=True, text=True,
    )
    assert result.stdout.strip() == "22050"


def test_convert_with_sample_rate_original(converter, wav_file):
    output = converter.convert(wav_file, "mp3", {"sample_rate": "original"})
    assert output.exists()
    assert output.stat().st_size > 0


def test_convert_flac_compression_level(converter, wav_file):
    output_0 = converter.convert(wav_file, "flac", {"compression_level": 0})
    size_0 = output_0.stat().st_size
    output_12 = converter.convert(wav_file, "flac", {"compression_level": 12})
    size_12 = output_12.stat().st_size
    assert size_12 <= size_0


def test_convert_wav_bit_depth_24(converter, wav_file):
    output = converter.convert(wav_file, "wav", {"bit_depth": "24"})
    assert output.exists()
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name",
         "-of", "csv=p=0", str(output)],
        capture_output=True, text=True,
    )
    assert result.stdout.strip() == "pcm_s24le"


def test_convert_with_normalize(converter, wav_file):
    output = converter.convert(wav_file, "mp3", {"normalize": True})
    assert output.exists()
    assert output.stat().st_size > 0


def test_convert_with_normalize_false(converter, wav_file):
    output = converter.convert(wav_file, "mp3", {"normalize": False})
    assert output.exists()
    assert output.stat().st_size > 0
