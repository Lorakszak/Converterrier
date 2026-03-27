# Converterrier — Next Steps

Suggested improvements roughly ordered by impact and effort.

## Short-term (low effort, high value)

- **Install Pandoc** on your machine (`sudo dnf install pandoc`) to enable document conversion
- **Add SVG input support** — use FFmpeg or `cairosvg` to convert SVG to raster formats (excluded from MVP)
- **Error toasts in the UI** — replace the plain error banner with dismissible toast notifications
- **Drag & drop visual feedback** — show a file type icon preview when dragging over the drop zone
- **Remember last used settings** — persist quality/bitrate preferences in localStorage

## Medium-term (moderate effort)

- **Progress indicator for large files** — add WebSocket or SSE to report FFmpeg/Pandoc progress in real-time instead of just a spinner
- **Conversion history** — show a list of recent conversions with re-download links (stored in-memory, not a database)
- **Frontend tests** — add Vitest + Vue Test Utils for component testing
- **Dark/light theme toggle** — the CSS variables are already set up for theming, just needs a toggle and a light palette
- **File preview** — show image thumbnails, audio waveform, or video frame before conversion
- **Advanced video settings** — trim start/end time, extract audio track, select codec

## Longer-term (larger effort)

- **Queue system for large files** — use background tasks with a simple in-memory queue so the UI doesn't block during long video conversions
- **Watched folder mode** — monitor a directory and auto-convert new files matching a rule
- **Plugin system** — let users add custom converters (e.g., HEIC, AVIF, epub) by dropping a Python module into a plugins directory
- **PyPI / pip packaging** — publish to PyPI so users can `pip install converterrier` or `uv tool install converterrier`
- **Desktop packaging** — bundle with PyInstaller or Briefcase for a downloadable executable that includes Python + deps
- **HEIC/HEIF support** — add `pillow-heif` for Apple image format support (very commonly requested)
- **Animated WebP** — support animated WebP to/from GIF conversion
