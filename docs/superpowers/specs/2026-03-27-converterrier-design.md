# Converterrier — Design Spec

Local file format converter with a browser-based UI. Runs entirely on the user's machine — no uploads, no external services.

## Stack

- **Backend:** Python, FastAPI, uvicorn
- **Frontend:** Vue 3, Vite
- **Conversion engines:** Pillow (images), FFmpeg via subprocess (video/audio), Pandoc via subprocess (documents)
- **Packaging:** pip-installable Python package with CLI entry point
- **License:** GPL-3.0

## Architecture

```
User runs: converterrier [--port 8000]
         │
         ▼
   CLI entry point (Python)
         │
         ├── Starts FastAPI server (uvicorn)
         ├── Opens browser to http://localhost:<port>
         │
         ▼
   FastAPI application
         │
         ├── GET /           → Serves Vue SPA (static files)
         ├── GET /api/formats → Returns supported format map
         ├── POST /api/convert → Accepts file + target format + settings, returns converted file
         ├── POST /api/convert/batch → Multiple files, returns ZIP
         └── GET /api/health  → Status + external tool availability
```

- FastAPI serves the built Vue frontend from a `static/` directory
- Conversion is synchronous (spinner in the UI)
- Uploaded files go to a temp directory, converted file returned as streaming download, temp files cleaned up
- No database, no auth — local tool

## Project Structure

```
converterrier/
├── pyproject.toml
├── src/
│   └── converterrier/
│       ├── __init__.py
│       ├── cli.py                  # CLI entry point — parse args, start server, open browser
│       ├── app.py                  # FastAPI app factory
│       ├── routes/
│       │   ├── convert.py          # POST /api/convert, POST /api/convert/batch
│       │   └── formats.py          # GET /api/formats
│       ├── converters/
│       │   ├── base.py             # Base converter interface
│       │   ├── image.py            # Pillow-based image conversion
│       │   ├── video.py            # FFmpeg video conversion
│       │   ├── audio.py            # FFmpeg audio conversion
│       │   └── document.py         # Pandoc document conversion
│       ├── models.py               # Pydantic models (settings, format maps)
│       └── static/                 # Built Vue frontend (generated, gitignored)
├── frontend/
│   ├── package.json
│   ├── vite.config.js              # Proxy /api to FastAPI in dev mode
│   ├── index.html
│   └── src/
│       ├── App.vue                 # Root component
│       ├── main.js                 # Vue app entry
│       ├── components/
│       │   ├── FileUpload.vue      # Drag & drop + file picker
│       │   ├── FormatSelector.vue  # Target format dropdown
│       │   ├── SettingsPanel.vue   # Basic conversion settings
│       │   ├── ConvertButton.vue   # Triggers conversion + download
│       │   └── BatchMode.vue       # Multi-file batch UI
│       └── assets/
│           └── styles.css
└── tests/
    ├── test_converters/
    └── test_routes/
```

## Conversion Engine

Each converter follows a common interface:

```python
class BaseConverter:
    supported_formats: dict[str, list[str]]  # {"png": ["jpg", "webp", ...]}

    def convert(self, input_path: Path, output_format: str, settings: dict) -> Path
    def get_settings_schema(self, input_format: str, output_format: str) -> dict
```

### ImageConverter (Pillow)

- Settings: quality (1-100), resize (width × height, optional)
- Formats: PNG, JPG/JPEG, WEBP, GIF, BMP, TIFF, ICO
- SVG input: uses Pillow or falls back to FFmpeg

### VideoConverter (FFmpeg subprocess)

- Settings: resolution preset (720p/1080p/original), quality (CRF value)
- Formats: MP4, WEBM, AVI, MKV, MOV, animated GIF
- Runs via `subprocess.run()`, captures stderr for errors

### AudioConverter (FFmpeg subprocess)

- Settings: bitrate (128k/192k/256k/320k), channels (mono/stereo)
- Formats: MP3, WAV, OGG, FLAC, AAC, M4A

### DocumentConverter (Pandoc subprocess)

- Settings: none initially
- Formats: Markdown, PDF, HTML, DOCX, TXT
- PDF output requires a LaTeX engine (pdflatex/xelatex)

### Format detection

Uses file extension from uploaded filename, validated against the supported formats map.

## API Design

### GET /api/formats

Returns the full format map with available settings per format pair:

```json
{
  "image": {
    "png": {
      "targets": ["jpg", "webp", "gif", "bmp", "tiff", "ico"],
      "settings": {
        "quality": {"type": "range", "min": 1, "max": 100, "default": 85},
        "resize": {"type": "dimensions", "optional": true}
      }
    }
  },
  "video": {},
  "audio": {},
  "document": {}
}
```

Frontend dynamically populates dropdowns and settings from this response.

### POST /api/convert

Multipart form upload:
- `file`: the uploaded file
- `target_format`: string (e.g., `"webp"`)
- `settings`: JSON string with converter-specific options (optional)

Returns: converted file as streaming download with `Content-Disposition: attachment`.

### POST /api/convert/batch

Same fields but accepts multiple files. Returns a ZIP archive containing all converted files.

### GET /api/health

```json
{
  "status": "ok",
  "ffmpeg": true,
  "pandoc": true,
  "pandoc_pdf": true
}
```

## Frontend UI

Single-page Vue 3 application:

1. **Header** — app name, logo, health status indicators (FFmpeg/Pandoc/LaTeX)
2. **Tab bar** — Single File / Batch Mode toggle
3. **Drop zone** — drag & drop area or click to browse files
4. **File info** — shows filename, size, detected format badge
5. **Format selector** — dropdown populated from /api/formats based on input type
6. **Settings panel** — inline contextual settings (quality slider, resolution, bitrate, etc.)
7. **Convert button** — triggers conversion, shows spinner, downloads result
8. **Footer** — "All conversions happen locally on your machine"

Batch mode: same flow but multi-file selection, shows list of files, converts all to same target format, downloads as ZIP.

## Error Handling

### External tool checks

All three external dependencies are checked on startup and reported via `/api/health`:

- **FFmpeg missing** → video and audio conversion disabled, warning in UI
- **Pandoc missing** → document conversion disabled, warning in UI
- **LaTeX engine missing** → PDF output disabled, other document conversions still work, warning in UI

### File errors

- Max upload size: 2GB default (configurable via `--max-size` CLI flag)
- Unsupported format pair → 400 with clear message
- Corrupted/unreadable file → 422 with details

### Conversion failures

- FFmpeg/Pandoc non-zero exit → capture stderr, return 500 with tool's error message
- Temp files always cleaned up via `finally` / `tempfile.TemporaryDirectory`

### Not handling (YAGNI)

- No rate limiting (local tool)
- No auth (local tool)
- No queue/task system (synchronous is fine for MVP)
- No websocket progress tracking (spinner only for now)

## Supported Formats at Launch

| Category | Formats |
|----------|---------|
| Image | PNG, JPG/JPEG, WEBP, GIF, BMP, TIFF, SVG, ICO |
| Video | MP4, WEBM, AVI, MKV, MOV, animated GIF |
| Audio | MP3, WAV, OGG, FLAC, AAC, M4A |
| Document | Markdown, PDF, HTML, DOCX, TXT |
