# Converterrier

## Project Overview

Local file format converter with a browser-based UI. FastAPI backend + Vue 3 frontend, packaged as a pip-installable CLI tool.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, uvicorn, Pillow, FFmpeg (subprocess), Pandoc (subprocess)
- **Frontend:** Vue 3 (Composition API with `<script setup>`), Vite
- **Package manager:** uv (Python), npm (frontend)
- **Testing:** pytest + httpx (backend), no frontend tests yet

## Key Commands

```bash
uv sync                          # install deps
uv run pytest -v                 # run tests
uv run converterrier             # start the app
cd frontend && npm run build     # rebuild frontend into src/converterrier/static/
```

## Architecture

- `src/converterrier/app.py` — FastAPI app factory (`create_app()`)
- `src/converterrier/cli.py` — CLI entry point, parses args, starts uvicorn + opens browser
- `src/converterrier/converters/base.py` — abstract `BaseConverter` interface all converters implement
- `src/converterrier/converters/__init__.py` — converter registry (`get_converter_for_format`, `get_all_formats`)
- `src/converterrier/routes/convert.py` — handles file upload, conversion, and download (single + batch)
- Frontend is a Vue 3 SPA served as static files in production

## Conventions

- Converters follow the `BaseConverter` interface: `category`, `get_supported_formats()`, `get_settings_schema()`, `convert()`
- Settings schemas are self-describing dicts consumed by the frontend to render controls dynamically
- Routes use `tempfile.mkdtemp()` for uploads, `BackgroundTasks` for cleanup after response
- Frontend uses Composition API (`<script setup>`) and scoped CSS throughout
- No database, no auth — this is a local-only tool

## Testing

- Image converter tests use Pillow to generate test fixtures on the fly
- Audio/video tests generate fixtures with FFmpeg, skip if FFmpeg is not installed
- Document tests skip if Pandoc is not installed
- Route tests use FastAPI's `TestClient`
