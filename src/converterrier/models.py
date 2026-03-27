from pydantic import BaseModel


class ToolStatus(BaseModel):
    status: str = "ok"
    ffmpeg: bool = False
    pandoc: bool = False
    pandoc_pdf: bool = False
