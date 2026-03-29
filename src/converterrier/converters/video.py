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
            # --- Basic settings ---
            "resolution": {
                "type": "select",
                "options": ["original", "720p", "1080p"],
                "default": "original",
                "label": "Resolution",
                "formats": ["mp4", "webm", "avi", "mkv", "mov"],
            },
            "quality": {
                "type": "range",
                "min": 18,
                "max": 51,
                "default": 23,
                "label": "Quality (CRF)",
                "formats": ["mp4", "webm", "avi", "mkv", "mov"],
            },
            # --- Advanced settings ---
            "preset": {
                "type": "select",
                "options": [
                    "ultrafast", "superfast", "veryfast", "faster",
                    "fast", "medium", "slow", "slower", "veryslow",
                ],
                "default": "medium",
                "label": "Preset",
                "advanced": True,
                "formats": ["mp4", "avi", "mkv", "mov"],
            },
            "tune": {
                "type": "select",
                "options": [
                    "none", "film", "animation", "grain",
                    "stillimage", "fastdecode", "zerolatency",
                ],
                "default": "none",
                "label": "Tune",
                "advanced": True,
                "formats": ["mp4", "avi", "mkv", "mov"],
            },
            "fps": {
                "type": "select",
                "options": ["original", "24", "25", "30", "60"],
                "default": "original",
                "label": "Frame rate",
                "advanced": True,
                "formats": ["mp4", "webm", "avi", "mkv", "mov"],
            },
            "strip_audio": {
                "type": "checkbox",
                "default": False,
                "label": "Strip audio",
                "advanced": True,
                "formats": ["mp4", "webm", "avi", "mkv", "mov"],
            },
            "gif_fps": {
                "type": "select",
                "options": ["5", "10", "15", "20", "25"],
                "default": "10",
                "label": "GIF frame rate",
                "advanced": True,
                "formats": ["gif"],
            },
            "gif_width": {
                "type": "select",
                "options": ["320", "480", "640", "original"],
                "default": "480",
                "label": "GIF width",
                "advanced": True,
                "formats": ["gif"],
            },
        }

    def convert(self, input_path: Path, output_format: str, settings: dict) -> Path:
        output_path = self._output_path(input_path, output_format)
        if output_path == input_path:
            output_path = input_path.parent / f"{input_path.stem}_converted.{output_format}"

        cmd = ["ffmpeg", "-y", "-i", str(input_path)]

        if output_format == "gif":
            gif_fps = settings.get("gif_fps", "10")
            gif_width = settings.get("gif_width", "480")
            if gif_width == "original":
                vf = f"fps={gif_fps},split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
            else:
                vf = f"fps={gif_fps},scale={gif_width}:-1:flags=lanczos"
            cmd += ["-vf", vf]
        else:
            # Resolution
            resolution = settings.get("resolution", "original")
            if resolution in _RESOLUTION_MAP:
                scale = _RESOLUTION_MAP[resolution]
                cmd += ["-vf", f"scale={scale}:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2"]

            # CRF quality
            crf = settings.get("quality", 23)
            cmd += ["-crf", str(crf)]

            # Preset (x264/x265 containers)
            preset = settings.get("preset", "medium")
            if preset != "medium":
                cmd += ["-preset", preset]

            # Tune
            tune = settings.get("tune", "none")
            if tune != "none":
                cmd += ["-tune", tune]

            # Frame rate
            fps = settings.get("fps", "original")
            if fps != "original":
                cmd += ["-r", fps]

            # Strip audio
            if settings.get("strip_audio"):
                cmd += ["-an"]

        cmd.append(str(output_path))

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        return output_path
