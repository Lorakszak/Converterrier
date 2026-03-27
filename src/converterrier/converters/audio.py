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
            "bitrate": {
                "type": "select",
                "options": ["128k", "192k", "256k", "320k"],
                "default": "192k",
                "label": "Bitrate",
            },
            "channels": {
                "type": "select",
                "options": ["mono", "stereo"],
                "default": "stereo",
                "label": "Channels",
            },
        }

    def convert(self, input_path: Path, output_format: str, settings: dict) -> Path:
        output_path = self._output_path(input_path, output_format)

        cmd = ["ffmpeg", "-y", "-i", str(input_path)]

        bitrate = settings.get("bitrate", "192k")
        cmd += ["-b:a", bitrate]

        channels = settings.get("channels")
        if channels and channels in _CHANNELS_MAP:
            cmd += ["-ac", _CHANNELS_MAP[channels]]

        cmd.append(str(output_path))

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        return output_path
