from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from converterrier.routes.health import router as health_router
from converterrier.routes.formats import router as formats_router
from converterrier.routes.convert import router as convert_router

_STATIC_DIR = Path(__file__).parent / "static"


def create_app(max_size: int = 2 * 1024 * 1024 * 1024) -> FastAPI:
    app = FastAPI(title="Converterrier")
    app.state.max_size = max_size

    app.include_router(health_router)
    app.include_router(formats_router)
    app.include_router(convert_router)

    # Serve Vue SPA if static files exist (production)
    if _STATIC_DIR.exists() and any(_STATIC_DIR.iterdir()):
        app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")

    return app
