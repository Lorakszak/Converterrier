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
            # --- Basic settings (shown by default) ---
            "quality": {
                "type": "range",
                "min": 1,
                "max": 100,
                "default": 85,
                "label": "Quality",
                "formats": ["jpg", "webp"],
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
            # --- JPEG advanced ---
            "progressive": {
                "type": "checkbox",
                "default": False,
                "label": "Progressive",
                "advanced": True,
                "formats": ["jpg"],
            },
            "optimize": {
                "type": "checkbox",
                "default": False,
                "label": "Optimize",
                "advanced": True,
                "formats": ["jpg", "gif"],
            },
            "subsampling": {
                "type": "select",
                "options": ["auto", "4:4:4", "4:2:2", "4:2:0"],
                "default": "auto",
                "label": "Chroma subsampling",
                "advanced": True,
                "formats": ["jpg"],
            },
            # --- PNG advanced ---
            "compress_level": {
                "type": "range",
                "min": 0,
                "max": 9,
                "default": 6,
                "label": "Compression level",
                "advanced": True,
                "formats": ["png"],
            },
            # --- WebP advanced ---
            "lossless": {
                "type": "checkbox",
                "default": False,
                "label": "Lossless",
                "advanced": True,
                "formats": ["webp"],
            },
            "method": {
                "type": "range",
                "min": 0,
                "max": 6,
                "default": 4,
                "label": "Compression effort",
                "advanced": True,
                "formats": ["webp"],
            },
            # --- TIFF advanced ---
            "compression": {
                "type": "select",
                "options": ["raw", "tiff_lzw", "tiff_adobe_deflate", "packbits"],
                "default": "raw",
                "label": "Compression",
                "advanced": True,
                "formats": ["tiff"],
            },
            # --- GIF advanced ---
            "interlace": {
                "type": "checkbox",
                "default": True,
                "label": "Interlace",
                "advanced": True,
                "formats": ["gif"],
            },
        }

    _SUBSAMPLING_MAP: dict[str, int] = {
        "4:4:4": 0,
        "4:2:2": 1,
        "4:2:0": 2,
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

        if output_format in ("jpg", "jpeg"):
            save_kwargs["quality"] = settings.get("quality", 85)
            if settings.get("progressive"):
                save_kwargs["progressive"] = True
            if settings.get("optimize"):
                save_kwargs["optimize"] = True
            subsampling = settings.get("subsampling", "auto")
            if subsampling != "auto":
                save_kwargs["subsampling"] = self._SUBSAMPLING_MAP[subsampling]

        elif output_format == "webp":
            save_kwargs["quality"] = settings.get("quality", 85)
            if settings.get("lossless"):
                save_kwargs["lossless"] = True
            save_kwargs["method"] = settings.get("method", 4)

        elif output_format == "png":
            save_kwargs["compress_level"] = settings.get("compress_level", 6)

        elif output_format == "tiff":
            compression = settings.get("compression", "raw")
            if compression != "raw":
                save_kwargs["compression"] = compression

        elif output_format == "gif":
            if settings.get("optimize", False):
                save_kwargs["optimize"] = True
            if "interlace" in settings:
                save_kwargs["interlace"] = 1 if settings["interlace"] else 0

        img.save(output_path, format=pillow_format, **save_kwargs)
        return output_path
