# Converterrier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local file format converter with a browser-based UI, packaged as a pip-installable CLI tool.

**Architecture:** FastAPI backend serves a Vue 3 SPA and REST API. Conversion handled by Pillow (images), FFmpeg (video/audio), and Pandoc (documents) via a common converter interface. CLI entry point starts the server and opens the browser.

**Tech Stack:** Python 3.11+, FastAPI, uvicorn, Pillow, FFmpeg, Pandoc, Vue 3, Vite

**Note:** SVG input support is deferred from MVP — Pillow cannot read SVG natively and it would require an additional dependency (cairosvg or librsvg). All other formats from the spec are included.

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/converterrier/__init__.py`
- Create: `src/converterrier/routes/__init__.py`
- Create: `src/converterrier/converters/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/test_converters/__init__.py`
- Create: `tests/test_routes/__init__.py`
- Create: `.gitignore`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p src/converterrier/routes src/converterrier/converters src/converterrier/static
mkdir -p tests/test_converters tests/test_routes
mkdir -p frontend/src/components frontend/src/assets
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "converterrier"
version = "0.1.0"
description = "Local file format converter — images, video, audio, documents"
requires-python = ">=3.11"
license = "GPL-3.0-or-later"
dependencies = [
    "fastapi>=0.100",
    "uvicorn[standard]>=0.20",
    "pillow>=10.0",
    "python-multipart>=0.0.6",
]

[project.scripts]
converterrier = "converterrier.cli:main"

[dependency-groups]
dev = [
    "pytest>=7.0",
    "httpx>=0.24",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/converterrier"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
.venv/

# Node
node_modules/
frontend/dist/

# Built frontend served by FastAPI
src/converterrier/static/*
!src/converterrier/static/.gitkeep

# Temp/IDE
.idea/
.vscode/
*.swp
.DS_Store

# Superpowers
.superpowers/
```

- [ ] **Step 4: Create __init__.py files**

`src/converterrier/__init__.py`:
```python
"""Converterrier — local file format converter."""

__version__ = "0.1.0"
```

Create empty `__init__.py` in:
- `src/converterrier/routes/__init__.py`
- `tests/__init__.py`
- `tests/test_converters/__init__.py`
- `tests/test_routes/__init__.py`

Create a `.gitkeep` in `src/converterrier/static/`.

- [ ] **Step 5: Install dependencies**

```bash
uv sync
```

- [ ] **Step 6: Verify setup**

```bash
uv run python -c "import converterrier; print(converterrier.__version__)"
```

Expected: `0.1.0`

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .gitignore src/ tests/
git commit -m "feat: project scaffolding with pyproject.toml and directory structure"
```

---

### Task 2: Pydantic Models and Tool Detection

**Files:**
- Create: `src/converterrier/models.py`
- Create: `src/converterrier/tools.py`
- Create: `tests/test_tools.py`

- [ ] **Step 1: Write failing tests for tool detection**

`tests/test_tools.py`:
```python
from converterrier.tools import check_tools, ToolStatus


def test_check_tools_returns_tool_status():
    result = check_tools()
    assert isinstance(result, ToolStatus)
    assert isinstance(result.ffmpeg, bool)
    assert isinstance(result.pandoc, bool)
    assert isinstance(result.pandoc_pdf, bool)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_tools.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'converterrier.tools'`

- [ ] **Step 3: Implement models and tool detection**

`src/converterrier/models.py`:
```python
from pydantic import BaseModel


class ToolStatus(BaseModel):
    status: str = "ok"
    ffmpeg: bool = False
    pandoc: bool = False
    pandoc_pdf: bool = False
```

`src/converterrier/tools.py`:
```python
import shutil

from converterrier.models import ToolStatus


def check_tools() -> ToolStatus:
    return ToolStatus(
        ffmpeg=shutil.which("ffmpeg") is not None,
        pandoc=shutil.which("pandoc") is not None,
        pandoc_pdf=(
            shutil.which("pdflatex") is not None
            or shutil.which("xelatex") is not None
        ),
    )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_tools.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/converterrier/models.py src/converterrier/tools.py tests/test_tools.py
git commit -m "feat: add Pydantic models and external tool detection"
```

---

### Task 3: Base Converter Interface

**Files:**
- Create: `src/converterrier/converters/base.py`

- [ ] **Step 1: Write the base converter**

`src/converterrier/converters/base.py`:
```python
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
```

- [ ] **Step 2: Verify it imports**

```bash
uv run python -c "from converterrier.converters.base import BaseConverter; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/converterrier/converters/base.py
git commit -m "feat: add base converter abstract interface"
```

---

### Task 4: Image Converter

**Files:**
- Create: `src/converterrier/converters/image.py`
- Create: `tests/test_converters/test_image.py`

- [ ] **Step 1: Write failing tests**

`tests/test_converters/test_image.py`:
```python
import pytest
from PIL import Image
from pathlib import Path

from converterrier.converters.image import ImageConverter


@pytest.fixture
def converter():
    return ImageConverter()


@pytest.fixture
def png_file(tmp_path):
    path = tmp_path / "test.png"
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))
    img.save(path, format="PNG")
    return path


def test_category(converter):
    assert converter.category == "image"


def test_supported_formats_has_png(converter):
    formats = converter.get_supported_formats()
    assert "png" in formats
    assert "jpg" in formats["png"]


def test_settings_schema_has_quality(converter):
    schema = converter.get_settings_schema("png")
    assert "quality" in schema
    assert schema["quality"]["type"] == "range"


def test_convert_png_to_jpg(converter, png_file):
    output = converter.convert(png_file, "jpg", {})
    assert output.exists()
    assert output.suffix == ".jpg"
    img = Image.open(output)
    assert img.format == "JPEG"


def test_convert_with_quality(converter, png_file):
    output = converter.convert(png_file, "webp", {"quality": 50})
    assert output.exists()
    assert output.suffix == ".webp"


def test_convert_with_resize(converter, png_file):
    output = converter.convert(png_file, "jpg", {"resize_width": 50, "resize_height": 50})
    assert output.exists()
    img = Image.open(output)
    assert img.size == (50, 50)


def test_convert_rgba_to_jpg_strips_alpha(converter, png_file):
    output = converter.convert(png_file, "jpg", {})
    img = Image.open(output)
    assert img.mode == "RGB"


def test_convert_to_ico(converter, tmp_path):
    path = tmp_path / "large.png"
    img = Image.new("RGBA", (512, 512), color=(0, 255, 0, 255))
    img.save(path, format="PNG")
    output = converter.convert(path, "ico", {})
    assert output.exists()
    assert output.suffix == ".ico"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_converters/test_image.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'converterrier.converters.image'`

- [ ] **Step 3: Implement ImageConverter**

`src/converterrier/converters/image.py`:
```python
from pathlib import Path

from PIL import Image

from .base import BaseConverter

# All formats that can be both input and output via Pillow
_ALL_FORMATS = ["png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "ico"]

# Pillow format name mapping (extension -> Pillow format string)
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

# Formats that support quality parameter
_QUALITY_FORMATS = {"jpg", "jpeg", "webp"}

# Max dimension for ICO output
_ICO_MAX_SIZE = 256


class ImageConverter(BaseConverter):
    @property
    def category(self) -> str:
        return "image"

    def get_supported_formats(self) -> dict[str, list[str]]:
        formats = {}
        for fmt in _ALL_FORMATS:
            if fmt == "jpeg":
                continue  # jpg and jpeg are the same, only list jpg
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

        # Handle resize
        width = settings.get("resize_width")
        height = settings.get("resize_height")
        if width and height:
            img = img.resize((int(width), int(height)))

        # ICO requires max 256x256
        if output_format == "ico" and (img.width > _ICO_MAX_SIZE or img.height > _ICO_MAX_SIZE):
            img.thumbnail((_ICO_MAX_SIZE, _ICO_MAX_SIZE))

        # JPEG doesn't support alpha — convert RGBA to RGB
        pillow_format = _PILLOW_FORMAT[output_format]
        if pillow_format == "JPEG" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Build save kwargs
        save_kwargs: dict = {}
        if output_format in _QUALITY_FORMATS:
            save_kwargs["quality"] = settings.get("quality", 85)

        img.save(output_path, format=pillow_format, **save_kwargs)
        return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_converters/test_image.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add src/converterrier/converters/image.py tests/test_converters/test_image.py
git commit -m "feat: add image converter with Pillow backend"
```

---

### Task 5: Audio Converter

**Files:**
- Create: `src/converterrier/converters/audio.py`
- Create: `tests/test_converters/test_audio.py`

- [ ] **Step 1: Write failing tests**

`tests/test_converters/test_audio.py`:
```python
import subprocess
import pytest
from pathlib import Path

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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_converters/test_audio.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'converterrier.converters.audio'`

- [ ] **Step 3: Implement AudioConverter**

`src/converterrier/converters/audio.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_converters/test_audio.py -v
```

Expected: all PASS (or skipped if FFmpeg not installed)

- [ ] **Step 5: Commit**

```bash
git add src/converterrier/converters/audio.py tests/test_converters/test_audio.py
git commit -m "feat: add audio converter with FFmpeg backend"
```

---

### Task 6: Video Converter

**Files:**
- Create: `src/converterrier/converters/video.py`
- Create: `tests/test_converters/test_video.py`

- [ ] **Step 1: Write failing tests**

`tests/test_converters/test_video.py`:
```python
import subprocess
import pytest
from pathlib import Path

from converterrier.converters.video import VideoConverter


@pytest.fixture
def converter():
    return VideoConverter()


@pytest.fixture
def mp4_file(tmp_path):
    path = tmp_path / "test.mp4"
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=1:size=320x240:rate=1",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
            "-c:v", "libx264", "-c:a", "aac", "-shortest",
            str(path),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip("FFmpeg not available or missing codecs")
    return path


def test_category(converter):
    assert converter.category == "video"


def test_supported_formats_has_mp4(converter):
    formats = converter.get_supported_formats()
    assert "mp4" in formats
    assert "webm" in formats["mp4"]


def test_settings_schema_has_resolution(converter):
    schema = converter.get_settings_schema("mp4")
    assert "resolution" in schema
    assert "quality" in schema


def test_convert_mp4_to_webm(converter, mp4_file):
    output = converter.convert(mp4_file, "webm", {})
    assert output.exists()
    assert output.suffix == ".webm"
    assert output.stat().st_size > 0


def test_convert_with_resolution(converter, mp4_file):
    output = converter.convert(mp4_file, "mkv", {"resolution": "720p"})
    assert output.exists()
    assert output.suffix == ".mkv"


def test_convert_to_gif(converter, mp4_file):
    output = converter.convert(mp4_file, "gif", {})
    assert output.exists()
    assert output.suffix == ".gif"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_converters/test_video.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'converterrier.converters.video'`

- [ ] **Step 3: Implement VideoConverter**

`src/converterrier/converters/video.py`:
```python
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

        # Resolution scaling
        resolution = settings.get("resolution", "original")
        if resolution in _RESOLUTION_MAP:
            scale = _RESOLUTION_MAP[resolution]
            # scale2div ensures dimensions are divisible by 2
            cmd += ["-vf", f"scale={scale}:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2"]

        # Quality (CRF) — not applicable to GIF output
        if output_format != "gif":
            crf = settings.get("quality", 23)
            cmd += ["-crf", str(crf)]

        # GIF-specific: palette for better quality
        if output_format == "gif":
            cmd += ["-vf", "fps=10,scale=480:-1:flags=lanczos"]

        cmd.append(str(output_path))

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_converters/test_video.py -v
```

Expected: all PASS (or skipped if FFmpeg not installed)

- [ ] **Step 5: Commit**

```bash
git add src/converterrier/converters/video.py tests/test_converters/test_video.py
git commit -m "feat: add video converter with FFmpeg backend"
```

---

### Task 7: Document Converter

**Files:**
- Create: `src/converterrier/converters/document.py`
- Create: `tests/test_converters/test_document.py`

- [ ] **Step 1: Write failing tests**

`tests/test_converters/test_document.py`:
```python
import subprocess
import pytest
from pathlib import Path

from converterrier.converters.document import DocumentConverter


@pytest.fixture
def converter():
    return DocumentConverter()


@pytest.fixture
def md_file(tmp_path):
    path = tmp_path / "test.md"
    path.write_text("# Hello\n\nThis is a **test** document.\n")
    return path


@pytest.fixture
def txt_file(tmp_path):
    path = tmp_path / "test.txt"
    path.write_text("Hello, this is plain text.\n")
    return path


def _pandoc_available():
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def test_category(converter):
    assert converter.category == "document"


def test_supported_formats_has_md(converter):
    formats = converter.get_supported_formats()
    assert "md" in formats
    assert "html" in formats["md"]


def test_settings_schema_is_empty(converter):
    schema = converter.get_settings_schema("md")
    assert schema == {}


@pytest.mark.skipif(not _pandoc_available(), reason="Pandoc not installed")
def test_convert_md_to_html(converter, md_file):
    output = converter.convert(md_file, "html", {})
    assert output.exists()
    assert output.suffix == ".html"
    content = output.read_text()
    assert "<h1" in content or "Hello" in content


@pytest.mark.skipif(not _pandoc_available(), reason="Pandoc not installed")
def test_convert_txt_to_html(converter, txt_file):
    output = converter.convert(txt_file, "html", {})
    assert output.exists()
    content = output.read_text()
    assert "Hello" in content


@pytest.mark.skipif(not _pandoc_available(), reason="Pandoc not installed")
def test_convert_md_to_docx(converter, md_file):
    output = converter.convert(md_file, "docx", {})
    assert output.exists()
    assert output.suffix == ".docx"
    assert output.stat().st_size > 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_converters/test_document.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'converterrier.converters.document'`

- [ ] **Step 3: Implement DocumentConverter**

`src/converterrier/converters/document.py`:
```python
import subprocess
from pathlib import Path

from .base import BaseConverter

_ALL_FORMATS = ["md", "pdf", "html", "docx", "txt"]

# Pandoc input format names (extension -> pandoc format flag)
_PANDOC_INPUT = {
    "md": "markdown",
    "pdf": "pdf",
    "html": "html",
    "docx": "docx",
    "txt": "plain",
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

        # PDF needs a LaTeX engine — pandoc selects one automatically if available
        if output_format == "pdf":
            cmd += ["--pdf-engine=xelatex"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc failed: {result.stderr}")

        return output_path
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_converters/test_document.py -v
```

Expected: all PASS (or skipped if Pandoc not installed)

- [ ] **Step 5: Commit**

```bash
git add src/converterrier/converters/document.py tests/test_converters/test_document.py
git commit -m "feat: add document converter with Pandoc backend"
```

---

### Task 8: Converter Registry

**Files:**
- Modify: `src/converterrier/converters/__init__.py`
- Create: `tests/test_converters/test_registry.py`

- [ ] **Step 1: Write failing tests**

`tests/test_converters/test_registry.py`:
```python
from converterrier.converters import get_converter_for_format, get_all_formats


def test_get_converter_for_png():
    converter = get_converter_for_format("png")
    assert converter is not None
    assert converter.category == "image"


def test_get_converter_for_mp3():
    converter = get_converter_for_format("mp3")
    assert converter is not None
    assert converter.category == "audio"


def test_get_converter_for_mp4():
    converter = get_converter_for_format("mp4")
    assert converter is not None
    assert converter.category == "video"


def test_get_converter_for_md():
    converter = get_converter_for_format("md")
    assert converter is not None
    assert converter.category == "document"


def test_get_converter_for_unknown():
    converter = get_converter_for_format("xyz123")
    assert converter is None


def test_get_all_formats_has_categories():
    formats = get_all_formats()
    assert "image" in formats
    assert "audio" in formats
    assert "video" in formats
    assert "document" in formats
    assert "png" in formats["image"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_converters/test_registry.py -v
```

Expected: FAIL — `ImportError: cannot import name 'get_converter_for_format'`

- [ ] **Step 3: Implement the registry**

`src/converterrier/converters/__init__.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_converters/test_registry.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add src/converterrier/converters/__init__.py tests/test_converters/test_registry.py
git commit -m "feat: add converter registry with format lookup"
```

---

### Task 9: FastAPI App and Health Route

**Files:**
- Create: `src/converterrier/app.py`
- Create: `src/converterrier/routes/health.py`
- Create: `tests/test_routes/test_health.py`

- [ ] **Step 1: Write failing tests**

`tests/test_routes/test_health.py`:
```python
from fastapi.testclient import TestClient

from converterrier.app import create_app


def test_health_returns_status():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ffmpeg" in data
    assert "pandoc" in data
    assert "pandoc_pdf" in data
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_routes/test_health.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'converterrier.app'`

- [ ] **Step 3: Implement app factory and health route**

`src/converterrier/routes/health.py`:
```python
from fastapi import APIRouter

from converterrier.models import ToolStatus
from converterrier.tools import check_tools

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> ToolStatus:
    return check_tools()
```

`src/converterrier/app.py`:
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from converterrier.routes.health import router as health_router

_STATIC_DIR = Path(__file__).parent / "static"


def create_app(max_size: int = 2 * 1024 * 1024 * 1024) -> FastAPI:
    app = FastAPI(title="Converterrier")
    app.state.max_size = max_size

    app.include_router(health_router)

    # Serve Vue SPA if static files exist (production)
    if _STATIC_DIR.exists() and any(_STATIC_DIR.iterdir()):
        app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")

    return app
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_routes/test_health.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/converterrier/app.py src/converterrier/routes/health.py tests/test_routes/test_health.py
git commit -m "feat: add FastAPI app factory and health endpoint"
```

---

### Task 10: Formats Route

**Files:**
- Create: `src/converterrier/routes/formats.py`
- Create: `tests/test_routes/test_formats.py`
- Modify: `src/converterrier/app.py`

- [ ] **Step 1: Write failing tests**

`tests/test_routes/test_formats.py`:
```python
from fastapi.testclient import TestClient

from converterrier.app import create_app


def test_formats_returns_all_categories():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/formats")
    assert response.status_code == 200
    data = response.json()
    assert "image" in data
    assert "audio" in data
    assert "video" in data
    assert "document" in data


def test_formats_image_has_targets():
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/formats")
    data = response.json()
    png = data["image"]["png"]
    assert "targets" in png
    assert "jpg" in png["targets"]
    assert "settings" in png
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_routes/test_formats.py -v
```

Expected: FAIL — 404 (route not registered yet)

- [ ] **Step 3: Implement formats route**

`src/converterrier/routes/formats.py`:
```python
from fastapi import APIRouter

from converterrier.converters import get_all_formats

router = APIRouter(prefix="/api")


@router.get("/formats")
def formats() -> dict:
    return get_all_formats()
```

- [ ] **Step 4: Register the router in app.py**

Add to `src/converterrier/app.py`, after the health router import:

```python
from converterrier.routes.formats import router as formats_router
```

And in `create_app()`, after `app.include_router(health_router)`:

```python
    app.include_router(formats_router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_routes/test_formats.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add src/converterrier/routes/formats.py src/converterrier/app.py tests/test_routes/test_formats.py
git commit -m "feat: add formats endpoint returning all supported conversions"
```

---

### Task 11: Single File Convert Route

**Files:**
- Create: `src/converterrier/routes/convert.py`
- Create: `tests/test_routes/test_convert.py`
- Modify: `src/converterrier/app.py`

- [ ] **Step 1: Write failing tests**

`tests/test_routes/test_convert.py`:
```python
import io
from PIL import Image
from fastapi.testclient import TestClient

from converterrier.app import create_app


def _make_png_bytes() -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def test_convert_png_to_jpg():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.png", _make_png_bytes(), "image/png")},
        data={"target_format": "jpg"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert "test.jpg" in response.headers["content-disposition"]
    # Verify it's a valid JPEG
    img = Image.open(io.BytesIO(response.content))
    assert img.format == "JPEG"


def test_convert_with_settings():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.png", _make_png_bytes(), "image/png")},
        data={"target_format": "webp", "settings": '{"quality": 50}'},
    )
    assert response.status_code == 200


def test_convert_unsupported_format():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.xyz", b"not a real file", "application/octet-stream")},
        data={"target_format": "jpg"},
    )
    assert response.status_code == 400


def test_convert_unsupported_target():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.png", _make_png_bytes(), "image/png")},
        data={"target_format": "mp3"},
    )
    assert response.status_code == 400


def test_convert_file_too_large():
    app = create_app(max_size=10)  # 10 bytes max
    client = TestClient(app)
    response = client.post(
        "/api/convert",
        files={"file": ("test.png", _make_png_bytes(), "image/png")},
        data={"target_format": "jpg"},
    )
    assert response.status_code == 413
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_routes/test_convert.py -v
```

Expected: FAIL — 404 (route not registered) or import error

- [ ] **Step 3: Implement convert route**

`src/converterrier/routes/convert.py`:
```python
import json
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from converterrier.converters import get_converter_for_format

router = APIRouter(prefix="/api")


async def _save_upload(file: UploadFile, tmp_dir: Path, max_size: int) -> Path:
    """Save uploaded file to temp directory, enforcing size limit."""
    safe_name = Path(file.filename).name  # strip any path components
    path = tmp_dir / safe_name
    size = 0
    with open(path, "wb") as f:
        while chunk := await file.read(8192):
            size += len(chunk)
            if size > max_size:
                path.unlink(missing_ok=True)
                raise HTTPException(413, "File too large")
            f.write(chunk)
    return path


@router.post("/convert")
async def convert_file(
    request: Request,
    file: UploadFile,
    target_format: str = Form(...),
    settings: str = Form("{}"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        max_size = request.app.state.max_size
        input_path = await _save_upload(file, tmp_dir, max_size)

        input_ext = input_path.suffix.lstrip(".").lower()
        converter = get_converter_for_format(input_ext)
        if converter is None:
            raise HTTPException(400, f"Unsupported input format: {input_ext}")

        supported = converter.get_supported_formats()
        if target_format not in supported.get(input_ext, []):
            raise HTTPException(
                400, f"Cannot convert {input_ext} to {target_format}"
            )

        parsed_settings = json.loads(settings)
        output_path = converter.convert(input_path, target_format, parsed_settings)

        output_name = f"{input_path.stem}.{target_format}"

        # Clean up temp dir after response is sent
        background_tasks.add_task(shutil.rmtree, tmp_dir, True)

        return FileResponse(
            path=str(output_path),
            filename=output_name,
            media_type="application/octet-stream",
        )
    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(500, f"Conversion failed: {e}")
```

- [ ] **Step 4: Register the router in app.py**

Add to `src/converterrier/app.py`, after the formats router import:

```python
from converterrier.routes.convert import router as convert_router
```

And in `create_app()`, after `app.include_router(formats_router)`:

```python
    app.include_router(convert_router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_routes/test_convert.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add src/converterrier/routes/convert.py src/converterrier/app.py tests/test_routes/test_convert.py
git commit -m "feat: add single file convert endpoint"
```

---

### Task 12: Batch Convert Route

**Files:**
- Modify: `src/converterrier/routes/convert.py`
- Modify: `tests/test_routes/test_convert.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_routes/test_convert.py`:

```python
import zipfile


def test_batch_convert():
    app = create_app()
    client = TestClient(app)
    png1 = _make_png_bytes()
    png2 = _make_png_bytes()
    response = client.post(
        "/api/convert/batch",
        files=[
            ("files", ("img1.png", png1, "image/png")),
            ("files", ("img2.png", png2, "image/png")),
        ],
        data={"target_format": "jpg"},
    )
    assert response.status_code == 200
    assert "application/zip" in response.headers["content-type"]

    z = zipfile.ZipFile(io.BytesIO(response.content))
    names = z.namelist()
    assert len(names) == 2
    assert "img1.jpg" in names
    assert "img2.jpg" in names


def test_batch_convert_empty():
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/convert/batch",
        data={"target_format": "jpg"},
    )
    assert response.status_code == 422
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_routes/test_convert.py::test_batch_convert -v
```

Expected: FAIL — 404 or 405

- [ ] **Step 3: Implement batch convert endpoint**

Add to `src/converterrier/routes/convert.py`:

```python
import zipfile

@router.post("/convert/batch")
async def convert_batch(
    request: Request,
    files: list[UploadFile],
    target_format: str = Form(...),
    settings: str = Form("{}"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        max_size = request.app.state.max_size
        parsed_settings = json.loads(settings)

        output_paths: list[Path] = []
        for upload in files:
            input_path = await _save_upload(upload, tmp_dir, max_size)
            input_ext = input_path.suffix.lstrip(".").lower()

            converter = get_converter_for_format(input_ext)
            if converter is None:
                raise HTTPException(400, f"Unsupported input format: {input_ext}")

            supported = converter.get_supported_formats()
            if target_format not in supported.get(input_ext, []):
                raise HTTPException(
                    400, f"Cannot convert {input_ext} to {target_format}"
                )

            output_path = converter.convert(input_path, target_format, parsed_settings)
            output_paths.append(output_path)

        # Create ZIP
        zip_path = tmp_dir / "converted.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in output_paths:
                zf.write(path, path.name)

        background_tasks.add_task(shutil.rmtree, tmp_dir, True)

        return FileResponse(
            path=str(zip_path),
            filename="converted.zip",
            media_type="application/zip",
        )
    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(500, f"Batch conversion failed: {e}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_routes/test_convert.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add src/converterrier/routes/convert.py tests/test_routes/test_convert.py
git commit -m "feat: add batch convert endpoint with ZIP download"
```

---

### Task 13: CLI Entry Point

**Files:**
- Create: `src/converterrier/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

`tests/test_cli.py`:
```python
from unittest.mock import patch, MagicMock

from converterrier.cli import parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.port == 8000
    assert args.max_size == 2 * 1024 * 1024 * 1024


def test_parse_args_custom_port():
    args = parse_args(["--port", "3000"])
    assert args.port == 3000


def test_parse_args_custom_max_size():
    args = parse_args(["--max-size", "500"])
    assert args.max_size == 500 * 1024 * 1024  # MB to bytes
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'converterrier.cli'`

- [ ] **Step 3: Implement CLI**

`src/converterrier/cli.py`:
```python
import argparse
import sys
import webbrowser

import uvicorn

from converterrier.app import create_app


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="converterrier",
        description="Local file format converter",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=2048,
        help="Max upload size in MB (default: 2048)",
    )
    args = parser.parse_args(argv)
    # Convert MB to bytes
    args.max_size = args.max_size * 1024 * 1024
    return args


def main():
    args = parse_args()
    app = create_app(max_size=args.max_size)

    url = f"http://localhost:{args.port}"
    print(f"Starting Converterrier at {url}")
    webbrowser.open(url)

    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_cli.py -v
```

Expected: all PASS

- [ ] **Step 5: Verify the CLI entry point resolves**

```bash
uv run converterrier --help
```

Expected: prints help text with `--port` and `--max-size` options.

- [ ] **Step 6: Commit**

```bash
git add src/converterrier/cli.py tests/test_cli.py
git commit -m "feat: add CLI entry point with --port and --max-size flags"
```

---

### Task 14: Vue Frontend Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/assets/styles.css`

- [ ] **Step 1: Initialize Node project and install deps**

```bash
cd frontend
npm init -y
npm install vue
npm install -D vite @vitejs/plugin-vue
```

- [ ] **Step 2: Create vite.config.js**

`frontend/vite.config.js`:
```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  build: {
    outDir: '../src/converterrier/static',
    emptyOutDir: true,
  },
})
```

- [ ] **Step 3: Create index.html**

`frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Converterrier</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: Create main.js**

`frontend/src/main.js`:
```js
import { createApp } from 'vue'
import App from './App.vue'
import './assets/styles.css'

createApp(App).mount('#app')
```

- [ ] **Step 5: Create styles.css**

`frontend/src/assets/styles.css`:
```css
:root {
  --bg-primary: #1a1a2e;
  --bg-secondary: #16213e;
  --bg-card: #0f3460;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent: #3b82f6;
  --accent-hover: #2563eb;
  --success: #4ade80;
  --warning: #fbbf24;
  --error: #f87171;
  --border: rgba(255, 255, 255, 0.08);
  --radius: 8px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
}

button {
  cursor: pointer;
  border: none;
  font-family: inherit;
}

select, input {
  font-family: inherit;
}
```

- [ ] **Step 6: Create App.vue shell**

`frontend/src/App.vue`:
```vue
<script setup>
import { ref, onMounted } from 'vue'

const health = ref({ ffmpeg: false, pandoc: false, pandoc_pdf: false })
const formats = ref({})
const error = ref('')

onMounted(async () => {
  try {
    const [healthRes, formatsRes] = await Promise.all([
      fetch('/api/health'),
      fetch('/api/formats'),
    ])
    health.value = await healthRes.json()
    formats.value = await formatsRes.json()
  } catch (e) {
    error.value = 'Failed to connect to backend'
  }
})
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header-left">
        <span class="logo">🐕</span>
        <span class="app-name">Converterrier</span>
      </div>
      <div class="header-right">
        <span :class="['status', health.ffmpeg ? 'ok' : 'missing']">
          {{ health.ffmpeg ? '●' : '○' }} FFmpeg
        </span>
        <span :class="['status', health.pandoc ? 'ok' : 'missing']">
          {{ health.pandoc ? '●' : '○' }} Pandoc
        </span>
      </div>
    </header>

    <main class="main">
      <p v-if="error" class="error-banner">{{ error }}</p>
      <p v-else class="placeholder">Components coming next...</p>
    </main>

    <footer class="footer">
      All conversions happen locally on your machine — no files are uploaded anywhere
    </footer>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 16px 24px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo { font-size: 1.4rem; }
.app-name { font-size: 1.1rem; font-weight: 600; }

.header-right {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
}

.status.ok { color: var(--success); }
.status.missing { color: var(--error); }

.main {
  flex: 1;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;
}

.error-banner {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid var(--error);
  color: var(--error);
  padding: 12px 16px;
  border-radius: var(--radius);
}

.placeholder {
  text-align: center;
  color: var(--text-muted);
  padding: 60px 0;
}

.footer {
  padding: 12px 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.75rem;
}
</style>
```

- [ ] **Step 7: Add scripts to package.json**

Edit `frontend/package.json` to include:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

- [ ] **Step 8: Verify dev server starts**

Start the FastAPI backend in one terminal:
```bash
uv run uvicorn converterrier.app:create_app --factory --port 8000
```

Start the Vite dev server in another:
```bash
cd frontend && npm run dev
```

Open the Vite URL (usually http://localhost:5173). You should see the header with health status indicators and the footer. The status dots should reflect whether FFmpeg/Pandoc are installed on your system.

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: add Vue frontend scaffolding with header and health status"
```

---

### Task 15: FileUpload Component

**Files:**
- Create: `frontend/src/components/FileUpload.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Create FileUpload component**

`frontend/src/components/FileUpload.vue`:
```vue
<script setup>
import { ref } from 'vue'

const emit = defineEmits(['file-selected'])
const dragging = ref(false)
const fileInput = ref(null)

function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) emit('file-selected', file)
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (file) emit('file-selected', file)
}

function openFilePicker() {
  fileInput.value.click()
}
</script>

<template>
  <div
    class="dropzone"
    :class="{ dragging }"
    @dragover.prevent="dragging = true"
    @dragleave="dragging = false"
    @drop.prevent="onDrop"
    @click="openFilePicker"
  >
    <input
      ref="fileInput"
      type="file"
      hidden
      @change="onFileChange"
    />
    <div class="dropzone-icon">📁</div>
    <p class="dropzone-text">Drag & drop a file here</p>
    <p class="dropzone-hint">or <span class="link">browse files</span></p>
  </div>
</template>

<style scoped>
.dropzone {
  border: 2px dashed rgba(74, 111, 165, 0.6);
  border-radius: var(--radius);
  padding: 48px 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.dropzone:hover,
.dropzone.dragging {
  border-color: var(--accent);
  background: rgba(59, 130, 246, 0.05);
}

.dropzone-icon { font-size: 2.5rem; margin-bottom: 8px; }
.dropzone-text { font-size: 1rem; margin-bottom: 4px; }
.dropzone-hint { color: var(--text-muted); font-size: 0.85rem; }
.link { color: var(--accent); text-decoration: underline; }
</style>
```

- [ ] **Step 2: Wire FileUpload into App.vue**

Replace the `<script setup>` and `<template>` in `frontend/src/App.vue`:

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import FileUpload from './components/FileUpload.vue'

const health = ref({ ffmpeg: false, pandoc: false, pandoc_pdf: false })
const formats = ref({})
const error = ref('')
const selectedFile = ref(null)
const batchMode = ref(false)

const fileInfo = computed(() => {
  if (!selectedFile.value) return null
  const name = selectedFile.value.name
  const ext = name.split('.').pop().toLowerCase()
  const size = selectedFile.value.size
  let category = null
  for (const [cat, catFormats] of Object.entries(formats.value)) {
    if (ext in catFormats) {
      category = cat
      break
    }
  }
  return { name, ext, size, category }
})

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function onFileSelected(file) {
  selectedFile.value = file
  error.value = ''
}

function removeFile() {
  selectedFile.value = null
}

onMounted(async () => {
  try {
    const [healthRes, formatsRes] = await Promise.all([
      fetch('/api/health'),
      fetch('/api/formats'),
    ])
    health.value = await healthRes.json()
    formats.value = await formatsRes.json()
  } catch (e) {
    error.value = 'Failed to connect to backend'
  }
})
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="header-left">
        <span class="logo">🐕</span>
        <span class="app-name">Converterrier</span>
      </div>
      <div class="header-right">
        <span :class="['status', health.ffmpeg ? 'ok' : 'missing']">
          {{ health.ffmpeg ? '●' : '○' }} FFmpeg
        </span>
        <span :class="['status', health.pandoc ? 'ok' : 'missing']">
          {{ health.pandoc ? '●' : '○' }} Pandoc
        </span>
      </div>
    </header>

    <main class="main">
      <div class="tabs">
        <button :class="['tab', { active: !batchMode }]" @click="batchMode = false">
          Single File
        </button>
        <button :class="['tab', { active: batchMode }]" @click="batchMode = true">
          Batch Mode
        </button>
      </div>

      <div class="content-area">
        <p v-if="error" class="error-banner">{{ error }}</p>

        <template v-if="!batchMode">
          <FileUpload v-if="!selectedFile" @file-selected="onFileSelected" />

          <div v-else class="file-info">
            <div class="file-info-row">
              <div class="file-details">
                <span class="format-badge">{{ fileInfo.ext.toUpperCase() }}</span>
                <span class="file-name">{{ fileInfo.name }}</span>
                <span class="file-size">{{ formatFileSize(fileInfo.size) }}</span>
              </div>
              <button class="remove-btn" @click="removeFile">✕ Remove</button>
            </div>
            <p v-if="!fileInfo.category" class="warning">
              Unsupported file format
            </p>
          </div>
        </template>
      </div>
    </main>

    <footer class="footer">
      All conversions happen locally on your machine — no files are uploaded anywhere
    </footer>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 16px 24px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
}

.header-left { display: flex; align-items: center; gap: 10px; }
.logo { font-size: 1.4rem; }
.app-name { font-size: 1.1rem; font-weight: 600; }
.header-right { display: flex; gap: 16px; font-size: 0.85rem; }
.status.ok { color: var(--success); }
.status.missing { color: var(--error); }

.main {
  flex: 1;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 0;
}

.tab {
  padding: 8px 16px;
  background: transparent;
  color: var(--text-secondary);
  border-radius: var(--radius) var(--radius) 0 0;
  font-size: 0.85rem;
  font-weight: 500;
}

.tab.active {
  background: var(--bg-card);
  color: var(--text-primary);
}

.content-area {
  background: var(--bg-card);
  padding: 24px;
  border-radius: 0 var(--radius) var(--radius) var(--radius);
}

.error-banner {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid var(--error);
  color: var(--error);
  padding: 12px 16px;
  border-radius: var(--radius);
}

.file-info {
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.file-info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.file-details { display: flex; align-items: center; gap: 10px; }

.format-badge {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.file-name { font-size: 0.9rem; }
.file-size { color: var(--text-muted); font-size: 0.8rem; }

.remove-btn {
  background: transparent;
  color: var(--text-muted);
  font-size: 0.85rem;
  padding: 4px 8px;
  border-radius: 4px;
}

.remove-btn:hover { color: var(--error); }

.warning {
  color: var(--warning);
  font-size: 0.85rem;
  margin-top: 12px;
}

.footer {
  padding: 12px 24px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.75rem;
}
</style>
```

- [ ] **Step 3: Verify in browser**

Run the Vite dev server and check:
- Drop zone appears
- Dropping or picking a file shows file info (name, extension badge, size)
- "Remove" clears the file
- Tab switching works

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/FileUpload.vue frontend/src/App.vue
git commit -m "feat: add FileUpload component with drag and drop"
```

---

### Task 16: FormatSelector and SettingsPanel Components

**Files:**
- Create: `frontend/src/components/FormatSelector.vue`
- Create: `frontend/src/components/SettingsPanel.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Create FormatSelector component**

`frontend/src/components/FormatSelector.vue`:
```vue
<script setup>
const props = defineProps({
  targets: { type: Array, required: true },
  modelValue: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="format-selector">
    <label class="label">Convert to:</label>
    <select
      class="format-select"
      :value="modelValue"
      @change="emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>Select format...</option>
      <option v-for="fmt in targets" :key="fmt" :value="fmt">
        {{ fmt.toUpperCase() }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.format-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.format-select {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid rgba(74, 111, 165, 0.4);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.85rem;
}
</style>
```

- [ ] **Step 2: Create SettingsPanel component**

`frontend/src/components/SettingsPanel.vue`:
```vue
<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  schema: { type: Object, required: true },
})

const emit = defineEmits(['update:settings'])

// Build initial values from schema defaults
const values = reactive({})

watch(
  () => props.schema,
  (schema) => {
    // Reset values when schema changes
    Object.keys(values).forEach((k) => delete values[k])
    for (const [key, def] of Object.entries(schema)) {
      if (def.default !== undefined) {
        values[key] = def.default
      }
    }
    emit('update:settings', { ...values })
  },
  { immediate: true }
)

function onInput(key, value) {
  values[key] = value
  emit('update:settings', { ...values })
}
</script>

<template>
  <div v-if="Object.keys(schema).length" class="settings-panel">
    <div v-for="(def, key) in schema" :key="key" class="setting">
      <template v-if="!def.optional || values[key] !== undefined">
        <label class="setting-label">{{ def.label }}:</label>

        <!-- Range slider -->
        <template v-if="def.type === 'range'">
          <input
            type="range"
            :min="def.min"
            :max="def.max"
            :value="values[key] ?? def.default"
            class="range-input"
            @input="onInput(key, Number($event.target.value))"
          />
          <span class="range-value">{{ values[key] ?? def.default }}</span>
        </template>

        <!-- Select dropdown -->
        <template v-else-if="def.type === 'select'">
          <select
            class="select-input"
            :value="values[key] ?? def.default"
            @change="onInput(key, $event.target.value)"
          >
            <option v-for="opt in def.options" :key="opt" :value="opt">
              {{ opt }}
            </option>
          </select>
        </template>

        <!-- Number input -->
        <template v-else-if="def.type === 'number'">
          <input
            type="number"
            :value="values[key]"
            :placeholder="def.label"
            class="number-input"
            @input="onInput(key, $event.target.value ? Number($event.target.value) : undefined)"
          />
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.settings-panel {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.setting {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-label {
  color: var(--text-secondary);
  font-size: 0.85rem;
  white-space: nowrap;
}

.range-input {
  width: 100px;
  accent-color: var(--accent);
}

.range-value {
  color: var(--text-primary);
  font-size: 0.8rem;
  min-width: 2em;
}

.select-input {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid rgba(74, 111, 165, 0.4);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
}

.number-input {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid rgba(74, 111, 165, 0.4);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  width: 80px;
}
</style>
```

- [ ] **Step 3: Wire both into App.vue**

Add imports at the top of `<script setup>` in `App.vue`:

```js
import FormatSelector from './components/FormatSelector.vue'
import SettingsPanel from './components/SettingsPanel.vue'
```

Add reactive state:

```js
const targetFormat = ref('')
const settings = ref({})

const availableTargets = computed(() => {
  if (!fileInfo.value?.category || !fileInfo.value?.ext) return []
  const cat = formats.value[fileInfo.value.category]
  if (!cat || !cat[fileInfo.value.ext]) return []
  return cat[fileInfo.value.ext].targets
})

const settingsSchema = computed(() => {
  if (!fileInfo.value?.category || !fileInfo.value?.ext) return {}
  const cat = formats.value[fileInfo.value.category]
  if (!cat || !cat[fileInfo.value.ext]) return {}
  return cat[fileInfo.value.ext].settings
})
```

Update `removeFile` to also clear target/settings:

```js
function removeFile() {
  selectedFile.value = null
  targetFormat.value = ''
  settings.value = {}
}
```

Add below the file-info div inside the template (after the closing `</div>` of `file-info`, still inside `content-area`):

```html
            <div v-if="selectedFile && fileInfo?.category" class="conversion-row">
              <FormatSelector
                v-model="targetFormat"
                :targets="availableTargets"
              />
              <div v-if="targetFormat" class="settings-divider"></div>
              <SettingsPanel
                v-if="targetFormat"
                :schema="settingsSchema"
                @update:settings="settings = $event"
              />
            </div>
```

Add CSS for the new elements:

```css
.conversion-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.settings-divider {
  width: 1px;
  height: 24px;
  background: var(--border);
}
```

- [ ] **Step 4: Verify in browser**

- Select a file → format dropdown appears with valid targets
- Select a target format → settings controls appear (quality slider for images, bitrate dropdown for audio, etc.)
- Changing the file clears the format selection

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/FormatSelector.vue frontend/src/components/SettingsPanel.vue frontend/src/App.vue
git commit -m "feat: add FormatSelector and SettingsPanel components"
```

---

### Task 17: ConvertButton and Download Flow

**Files:**
- Create: `frontend/src/components/ConvertButton.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Create ConvertButton component**

`frontend/src/components/ConvertButton.vue`:
```vue
<script setup>
defineProps({
  disabled: { type: Boolean, default: false },
  converting: { type: Boolean, default: false },
})

const emit = defineEmits(['convert'])
</script>

<template>
  <button
    class="convert-btn"
    :class="{ converting }"
    :disabled="disabled || converting"
    @click="emit('convert')"
  >
    <template v-if="converting">
      <span class="spinner"></span> Converting...
    </template>
    <template v-else>
      Convert & Download
    </template>
  </button>
</template>

<style scoped>
.convert-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, var(--accent), var(--accent-hover));
  color: white;
  padding: 12px 48px;
  border-radius: var(--radius);
  font-weight: 600;
  font-size: 1rem;
  transition: opacity 0.2s;
}

.convert-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.convert-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
```

- [ ] **Step 2: Add convert logic and wire button into App.vue**

Add import:

```js
import ConvertButton from './components/ConvertButton.vue'
```

Add state:

```js
const converting = ref(false)
```

Add the convert function:

```js
async function doConvert() {
  if (!selectedFile.value || !targetFormat.value) return

  converting.value = true
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('target_format', targetFormat.value)
    formData.append('settings', JSON.stringify(settings.value))

    const response = await fetch('/api/convert', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Conversion failed')
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${selectedFile.value.name.replace(/\.[^.]+$/, '')}.${targetFormat.value}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = e.message
  } finally {
    converting.value = false
  }
}
```

Add the button in the template, after the `conversion-row` div:

```html
            <div v-if="selectedFile && targetFormat" class="convert-area">
              <ConvertButton
                :disabled="!targetFormat"
                :converting="converting"
                @convert="doConvert"
              />
            </div>
```

Add CSS:

```css
.convert-area {
  margin-top: 20px;
  text-align: center;
}
```

- [ ] **Step 3: Verify end-to-end in browser**

With both backend and frontend dev servers running:
1. Drop a PNG file
2. Select JPG as target
3. Adjust quality slider
4. Click "Convert & Download"
5. Browser should download the converted file

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ConvertButton.vue frontend/src/App.vue
git commit -m "feat: add ConvertButton with download flow"
```

---

### Task 18: BatchMode Component

**Files:**
- Create: `frontend/src/components/BatchMode.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Create BatchMode component**

`frontend/src/components/BatchMode.vue`:
```vue
<script setup>
import { ref } from 'vue'

const emit = defineEmits(['files-selected'])
const dragging = ref(false)
const fileInput = ref(null)

function onDrop(e) {
  dragging.value = false
  const files = Array.from(e.dataTransfer.files)
  if (files.length) emit('files-selected', files)
}

function onFileChange(e) {
  const files = Array.from(e.target.files)
  if (files.length) emit('files-selected', files)
}

function openFilePicker() {
  fileInput.value.click()
}
</script>

<template>
  <div
    class="dropzone"
    :class="{ dragging }"
    @dragover.prevent="dragging = true"
    @dragleave="dragging = false"
    @drop.prevent="onDrop"
    @click="openFilePicker"
  >
    <input
      ref="fileInput"
      type="file"
      multiple
      hidden
      @change="onFileChange"
    />
    <div class="dropzone-icon">📁</div>
    <p class="dropzone-text">Drag & drop multiple files here</p>
    <p class="dropzone-hint">or <span class="link">browse files</span></p>
  </div>
</template>

<style scoped>
.dropzone {
  border: 2px dashed rgba(74, 111, 165, 0.6);
  border-radius: var(--radius);
  padding: 48px 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.dropzone:hover,
.dropzone.dragging {
  border-color: var(--accent);
  background: rgba(59, 130, 246, 0.05);
}

.dropzone-icon { font-size: 2.5rem; margin-bottom: 8px; }
.dropzone-text { font-size: 1rem; margin-bottom: 4px; }
.dropzone-hint { color: var(--text-muted); font-size: 0.85rem; }
.link { color: var(--accent); text-decoration: underline; }
</style>
```

- [ ] **Step 2: Wire BatchMode into App.vue**

Add import:

```js
import BatchMode from './components/BatchMode.vue'
```

Add state:

```js
const selectedFiles = ref([])
```

Add computed for batch — detects category from first file:

```js
const batchInfo = computed(() => {
  if (!selectedFiles.value.length) return null
  const first = selectedFiles.value[0]
  const ext = first.name.split('.').pop().toLowerCase()
  let category = null
  for (const [cat, catFormats] of Object.entries(formats.value)) {
    if (ext in catFormats) {
      category = cat
      break
    }
  }
  return { ext, category, count: selectedFiles.value.length }
})

const batchTargets = computed(() => {
  if (!batchInfo.value?.category || !batchInfo.value?.ext) return []
  const cat = formats.value[batchInfo.value.category]
  if (!cat || !cat[batchInfo.value.ext]) return []
  return cat[batchInfo.value.ext].targets
})

const batchSettingsSchema = computed(() => {
  if (!batchInfo.value?.category || !batchInfo.value?.ext) return {}
  const cat = formats.value[batchInfo.value.category]
  if (!cat || !cat[batchInfo.value.ext]) return {}
  return cat[batchInfo.value.ext].settings
})
```

Add batch handlers:

```js
function onBatchFilesSelected(files) {
  selectedFiles.value = files
  targetFormat.value = ''
  settings.value = {}
  error.value = ''
}

function clearBatch() {
  selectedFiles.value = []
  targetFormat.value = ''
  settings.value = {}
}

async function doBatchConvert() {
  if (!selectedFiles.value.length || !targetFormat.value) return

  converting.value = true
  error.value = ''

  try {
    const formData = new FormData()
    for (const file of selectedFiles.value) {
      formData.append('files', file)
    }
    formData.append('target_format', targetFormat.value)
    formData.append('settings', JSON.stringify(settings.value))

    const response = await fetch('/api/convert/batch', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Batch conversion failed')
    }

    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'converted.zip'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = e.message
  } finally {
    converting.value = false
  }
}
```

Add batch template inside the `content-area`, after the single-file `</template>`:

```html
        <template v-if="batchMode">
          <BatchMode v-if="!selectedFiles.length" @files-selected="onBatchFilesSelected" />

          <template v-else>
            <div class="file-info">
              <div class="file-info-row">
                <div class="file-details">
                  <span class="format-badge">{{ batchInfo?.ext?.toUpperCase() }}</span>
                  <span class="file-name">{{ batchInfo?.count }} files selected</span>
                </div>
                <button class="remove-btn" @click="clearBatch">✕ Clear</button>
              </div>
              <ul class="batch-list">
                <li v-for="(f, i) in selectedFiles" :key="i" class="batch-item">
                  {{ f.name }} — {{ formatFileSize(f.size) }}
                </li>
              </ul>
            </div>

            <div v-if="batchInfo?.category" class="conversion-row">
              <FormatSelector v-model="targetFormat" :targets="batchTargets" />
              <div v-if="targetFormat" class="settings-divider"></div>
              <SettingsPanel
                v-if="targetFormat"
                :schema="batchSettingsSchema"
                @update:settings="settings = $event"
              />
            </div>

            <div v-if="targetFormat" class="convert-area">
              <ConvertButton
                :disabled="!targetFormat"
                :converting="converting"
                @convert="doBatchConvert"
              />
            </div>
          </template>
        </template>
```

Add CSS for batch list:

```css
.batch-list {
  list-style: none;
  margin-top: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.batch-item {
  padding: 4px 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
}

.batch-item:last-child {
  border-bottom: none;
}
```

- [ ] **Step 3: Verify batch mode in browser**

1. Switch to "Batch Mode" tab
2. Drop multiple PNG files
3. Select JPG as target
4. Click "Convert & Download"
5. Browser should download `converted.zip` containing all converted files

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/BatchMode.vue frontend/src/App.vue
git commit -m "feat: add batch mode with multi-file conversion and ZIP download"
```

---

### Task 19: Build Pipeline and Production Integration

**Files:**
- Modify: `frontend/package.json`
- Modify: `src/converterrier/app.py`

- [ ] **Step 1: Build the Vue frontend**

```bash
cd frontend && npm run build
```

Verify output exists:
```bash
ls ../src/converterrier/static/
```

Expected: `index.html`, `assets/` directory with JS and CSS bundles.

- [ ] **Step 2: Verify production mode works**

Start the app using the CLI:
```bash
uv run converterrier --port 8080
```

Browser should open to `http://localhost:8080` with the full working app served by FastAPI — no Vite dev server needed.

Test: upload a file, convert it, download it. Everything should work from the single FastAPI process.

- [ ] **Step 3: Run all tests**

```bash
uv run pytest -v
```

Expected: all tests pass. Fix any failures before proceeding.

- [ ] **Step 4: Commit**

```bash
git add src/converterrier/static/ frontend/package.json
git commit -m "feat: add frontend build pipeline for production serving"
```

- [ ] **Step 5: Final verification**

Clean install test:
```bash
uv run pip install -e .
converterrier --help
converterrier --port 9000
```

Verify the app starts, browser opens, and all conversion types work (image, audio, video, document — depending on which tools are installed).
