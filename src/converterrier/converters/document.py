import subprocess
from pathlib import Path

from .base import BaseConverter

_ALL_FORMATS = ["md", "pdf", "html", "docx", "txt"]

_PANDOC_INPUT = {
    "md": "markdown",
    "pdf": "pdf",
    "html": "html",
    "docx": "docx",
    "txt": "markdown",
}


class DocumentConverter(BaseConverter):
    @property
    def category(self) -> str:
        return "document"

    def get_supported_formats(self) -> dict[str, list[str]]:
        return {fmt: [f for f in _ALL_FORMATS if f != fmt] for fmt in _ALL_FORMATS}

    def get_settings_schema(self, input_format: str) -> dict:
        return {}

    def convert(self, input_path: Path, output_format: str, settings: dict) -> Path:
        output_path = self._output_path(input_path, output_format)

        input_format = input_path.suffix.lstrip(".").lower()
        pandoc_from = _PANDOC_INPUT.get(input_format, input_format)

        cmd = [
            "pandoc",
            str(input_path),
            "-f", pandoc_from,
            "-o", str(output_path),
        ]

        if output_format == "pdf":
            cmd += ["--pdf-engine=xelatex"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc failed: {result.stderr}")

        return output_path
