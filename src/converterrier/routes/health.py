from fastapi import APIRouter

from converterrier.models import ToolStatus
from converterrier.tools import check_tools

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> ToolStatus:
    return check_tools()
