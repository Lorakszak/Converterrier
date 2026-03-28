# Converterrier

Local tool for quick file format conversion across images, audio, video, text and more. Runs entirely on your machine - no uploads, no waiting. Supports dark/light theme, single and batch file conversion, and an About page listing all capabilities.

## Supported Formats

| Category | Formats |
|----------|---------|
| Image | PNG, JPG, WEBP, GIF, BMP, TIFF, ICO |
| Video | MP4, WEBM, AVI, MKV, MOV, animated GIF |
| Audio | MP3, WAV, OGG, FLAC, AAC, M4A |
| Document | Markdown, PDF, HTML, DOCX, TXT |

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** (only for frontend development)
- **FFmpeg** (required for video/audio conversion)
- **Pandoc** (required for document conversion)
- **LaTeX engine** such as `xelatex` or `pdflatex` (required for PDF output via Pandoc)

### Installing prerequisites on Fedora

```bash
sudo dnf install ffmpeg pandoc texlive-xetex
```

### Installing prerequisites on Ubuntu/Debian

```bash
sudo apt install ffmpeg pandoc texlive-xetex
```

### Installing prerequisites on macOS

```bash
brew install ffmpeg pandoc
brew install --cask mactex  # for PDF output
```

FFmpeg and Pandoc are optional - the app will gracefully disable conversion types when a tool is missing and show a warning in the UI.

## Quick Start

```bash
# Clone and install
git clone <repo-url> && cd converterrier
uv sync

# Run
uv run converterrier
```

This starts the server on `http://localhost:8000` and opens your browser automatically.

### CLI Options

```bash
uv run converterrier --port 3000        # custom port
uv run converterrier --max-size 500     # max upload size in MB (default: 2048)
```

## Development

### Backend

```bash
uv sync                                  # install dependencies
uv run pytest -v                         # run tests
uv run uvicorn converterrier.app:create_app --factory --reload --port 8000  # dev server
```

### Frontend

```bash
cd frontend
npm install                              # install dependencies
npm run dev                              # start Vite dev server (proxies /api to :8000)
npm run build                            # build for production (outputs to src/converterrier/static/)
```

During development, run the FastAPI backend on port 8000 and the Vite dev server separately. Vite proxies API requests to the backend automatically.

### Project Structure

```
converterrier/
├── pyproject.toml              # Python package config, CLI entry point
├── src/converterrier/
│   ├── cli.py                  # CLI entry point
│   ├── app.py                  # FastAPI app factory
│   ├── routes/                 # API endpoints
│   │   ├── health.py           # GET /api/health
│   │   ├── formats.py          # GET /api/formats
│   │   └── convert.py          # POST /api/convert, /api/convert/batch
│   ├── converters/             # Conversion backends
│   │   ├── base.py             # Abstract converter interface
│   │   ├── image.py            # Pillow
│   │   ├── audio.py            # FFmpeg
│   │   ├── video.py            # FFmpeg
│   │   └── document.py         # Pandoc
│   └── static/                 # Built Vue frontend
├── frontend/                   # Vue 3 + Vite source
└── tests/
```

## License

GPL-3.0-or-later
