import subprocess
from pathlib import Path

from .base import BaseConverter

_ALL_FORMATS = ["mp3", "wav", "ogg", "flac", "aac", "m4a"]

_CHANNELS_MAP = {
    "mono": "1",
    "stereo": "2",
}


class AudioConverter(BaseConverter):
    @property
    def category(self) -> str:
        return "audio"

    def get_supported_formats(self) -> dict[str, list[str]]:
        return {fmt: [f for f in _ALL_FORMATS if f != fmt] for fmt in _ALL_FORMATS}

    def get_settings_schema(self, input_format: str) -> dict:
        return {
            # --- Basic settings ---
            "bitrate": {
                "type": "select",
                "options": ["128k", "192k", "256k", "320k"],
                "default": "192k",
                "label": "Bitrate",
                "formats": ["mp3", "ogg", "aac", "m4a"],
            },
            "channels": {
                "type": "select",
                "options": ["mono", "stereo"],
                "default": "stereo",
                "label": "Channels",
            },
            # --- Advanced settings ---
            "sample_rate": {
                "type": "select",
                "options": ["original", "8000", "22050", "44100", "48000"],
                "default": "original",
                "label": "Sample rate (Hz)",
                "advanced": True,
            },
            "compression_level": {
                "type": "range",
                "min": 0,
                "max": 12,
                "default": 5,
                "label": "Compression level",
                "advanced": True,
                "formats": ["flac"],
            },
            "bit_depth": {
                "type": "select",
                "options": ["16", "24", "32"],
                "default": "16",
                "label": "Bit depth",
                "advanced": True,
                "formats": ["wav"],
            },
            "normalize": {
                "type": "checkbox",
                "default": False,
                "label": "Normalize volume",
                "advanced": True,
            },
        }

    _BIT_DEPTH_CODEC: dict[str, str] = {
        "16": "pcm_s16le",
        "24": "pcm_s24le",
        "32": "pcm_s32le",
    }

    def convert(self, input_path: Path, output_format: str, settings: dict) -> Path:
        output_path = self._output_path(input_path, output_format)
        if output_path == input_path:
            output_path = input_path.parent / f"{input_path.stem}_converted.{output_format}"

        cmd = ["ffmpeg", "-y", "-i", str(input_path)]

        # Bitrate (lossy formats only)
        if output_format in ("mp3", "ogg", "aac", "m4a"):
            bitrate = settings.get("bitrate", "192k")
            cmd += ["-b:a", bitrate]

        # Channels
        channels = settings.get("channels")
        if channels and channels in _CHANNELS_MAP:
            cmd += ["-ac", _CHANNELS_MAP[channels]]

        # Sample rate
        sample_rate = settings.get("sample_rate", "original")
        if sample_rate != "original":
            cmd += ["-ar", sample_rate]

        # FLAC compression level
        if output_format == "flac":
            compression_level = settings.get("compression_level", 5)
            cmd += ["-compression_level", str(compression_level)]

        # WAV bit depth
        if output_format == "wav":
            bit_depth = settings.get("bit_depth", "16")
            cmd += ["-c:a", self._BIT_DEPTH_CODEC[bit_depth]]

        # Volume normalization
        if settings.get("normalize"):
            cmd += ["-af", "loudnorm"]

        cmd.append(str(output_path))

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        return output_path
