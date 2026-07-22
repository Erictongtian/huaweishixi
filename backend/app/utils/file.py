import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import BusinessException


def validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise BusinessException("文件名不能为空")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise BusinessException(f"不支持的文件格式，仅允许 {', '.join(settings.ALLOWED_EXTENSIONS)}")

    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise BusinessException(f"文件大小超过限制，最大允许 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB")


async def save_upload_file(file: UploadFile) -> dict:
    validate_file(file)

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / filename
    content = await file.read()
    file_path.write_bytes(content)

    url = f"/uploads/{filename}"
    return {"url": url, "filename": filename, "size": len(content)}


def delete_file(url: str) -> None:
    if not url.startswith("/uploads/"):
        return
    filename = url.removeprefix("/uploads/")
    file_path = Path(settings.UPLOAD_DIR) / filename
    if file_path.exists():
        file_path.unlink()
