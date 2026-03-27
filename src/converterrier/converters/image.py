from pathlib import Path

from PIL import Image

from .base import BaseConverter

_ALL_FORMATS = ["png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "ico"]

_PILLOW_FORMAT = {
    "png": "PNG",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "webp": "WEBP",
    "gif": "GIF",
    "bmp": "BMP",
    "tiff": "TIFF",
    "ico": "ICO",
}

_QUALITY_FORMATS = {"jpg", "jpeg", "webp"}

_ICO_MAX_SIZE = 256


class ImageConverter(BaseConverter):
    @property
    def category(self) -> str:
        return "image"

    def get_supported_formats(self) -> dict[str, list[str]]:
        formats = {}
        for fmt in _ALL_FORMATS:
            if fmt == "jpeg":
                continue
            targets = [f for f in _ALL_FORMATS if f != fmt and f != "jpeg"]
            formats[fmt] = targets
        return formats

    def get_settings_schema(self, input_format: str) -> dict:
        return {
            "quality": {
                "type": "range",
                "min": 1,
                "max": 100,
                "default": 85,
                "label": "Quality",
            },
            "resize_width": {
                "type": "number",
                "optional": True,
                "label": "Width (px)",
            },
            "resize_height": {
                "type": "number",
                "optional": True,
                "label": "Height (px)",
            },
        }

    def convert(self, input_path: Path, output_format: str, settings: dict) -> Path:
        output_path = self._output_path(input_path, output_format)
        img = Image.open(input_path)

        width = settings.get("resize_width")
        height = settings.get("resize_height")
        if width and height:
            img = img.resize((int(width), int(height)))

        if output_format == "ico" and (img.width > _ICO_MAX_SIZE or img.height > _ICO_MAX_SIZE):
            img.thumbnail((_ICO_MAX_SIZE, _ICO_MAX_SIZE))

        pillow_format = _PILLOW_FORMAT[output_format]
        if pillow_format == "JPEG" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        save_kwargs: dict = {}
        if output_format in _QUALITY_FORMATS:
            save_kwargs["quality"] = settings.get("quality", 85)

        img.save(output_path, format=pillow_format, **save_kwargs)
        return output_path
