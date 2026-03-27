import subprocess
from pathlib import Path

from .base import BaseConverter

_ALL_FORMATS = ["mp4", "webm", "avi", "mkv", "mov", "gif"]

_RESOLUTION_MAP = {
    "720p": "1280:720",
    "1080p": "1920:1080",
}


class VideoConverter(BaseConverter):
    @property
    def category(self) -> str:
        return "video"

    def get_supported_formats(self) -> dict[str, list[str]]:
        return {fmt: [f for f in _ALL_FORMATS if f != fmt] for fmt in _ALL_FORMATS}

    def get_settings_schema(self, input_format: str) -> dict:
        return {
            "resolution": {
                "type": "select",
                "options": ["original", "720p", "1080p"],
                "default": "original",
                "label": "Resolution",
            },
            "quality": {
                "type": "range",
                "min": 18,
                "max": 51,
                "default": 23,
                "label": "Quality (CRF)",
            },
        }

    def convert(self, input_path: Path, output_format: str, settings: dict) -> Path:
        output_path = self._output_path(input_path, output_format)

        cmd = ["ffmpeg", "-y", "-i", str(input_path)]

        resolution = settings.get("resolution", "original")
        if resolution in _RESOLUTION_MAP:
            scale = _RESOLUTION_MAP[resolution]
            cmd += ["-vf", f"scale={scale}:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2"]

        if output_format != "gif":
            crf = settings.get("quality", 23)
            cmd += ["-crf", str(crf)]

        if output_format == "gif":
            cmd += ["-vf", "fps=10,scale=480:-1:flags=lanczos"]

        cmd.append(str(output_path))

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        return output_path
