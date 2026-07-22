from fastapi import APIRouter, Depends, UploadFile

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.base import ResponseBase
from app.utils.file import save_upload_file

router = APIRouter()


@router.post("/upload", response_model=ResponseBase)
async def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    result = await save_upload_file(file)
    return ResponseBase(data=result)
