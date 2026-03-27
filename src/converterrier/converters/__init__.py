from .base import BaseConverter
from .image import ImageConverter
from .audio import AudioConverter
from .video import VideoConverter
from .document import DocumentConverter

ALL_CONVERTERS: list[BaseConverter] = [
    ImageConverter(),
    AudioConverter(),
    VideoConverter(),
    DocumentConverter(),
]


def get_converter_for_format(input_format: str) -> BaseConverter | None:
    for converter in ALL_CONVERTERS:
        if input_format in converter.get_supported_formats():
            return converter
    return None


def get_all_formats() -> dict[str, dict]:
    formats: dict[str, dict] = {}
    for converter in ALL_CONVERTERS:
        category = converter.category
        formats[category] = {}
        for input_fmt, targets in converter.get_supported_formats().items():
            formats[category][input_fmt] = {
                "targets": targets,
                "settings": converter.get_settings_schema(input_fmt),
            }
    return formats
