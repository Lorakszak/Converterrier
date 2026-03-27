import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from converterrier.converters import get_converter_for_format

router = APIRouter(prefix="/api")


async def _save_upload(file: UploadFile, tmp_dir: Path, max_size: int) -> Path:
    """Save uploaded file to temp directory, enforcing size limit."""
    safe_name = Path(file.filename).name
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
