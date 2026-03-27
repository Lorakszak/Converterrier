from abc import ABC, abstractmethod
from pathlib import Path


class BaseConverter(ABC):
    @property
    @abstractmethod
    def category(self) -> str:
        """Category name: 'image', 'video', 'audio', or 'document'."""
        ...

    @abstractmethod
    def get_supported_formats(self) -> dict[str, list[str]]:
        """Return {input_format: [output_formats]}."""
        ...

    @abstractmethod
    def get_settings_schema(self, input_format: str) -> dict:
        """Return settings schema for the given input format."""
        ...

    @abstractmethod
    def convert(self, input_path: Path, output_format: str, settings: dict) -> Path:
        """Convert file and return path to the output file."""
        ...

    def _output_path(self, input_path: Path, output_format: str) -> Path:
        """Build the output path in the same directory as input."""
        return input_path.parent / f"{input_path.stem}.{output_format}"
