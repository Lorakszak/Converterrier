from fastapi import APIRouter

from converterrier.converters import get_all_formats

router = APIRouter(prefix="/api")


@router.get("/formats")
def formats() -> dict:
    return get_all_formats()
