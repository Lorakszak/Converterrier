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
