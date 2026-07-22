from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.base import ResponseBase, PageResponse
from app.schemas.user import ProfileUpdate, ChangePassword
from app.services.user_service import update_profile, change_password, get_my_devices
from app.services.review_service import get_review_stats

router = APIRouter()


@router.put("/me", response_model=ResponseBase)
async def update_profile_api(
    req: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await update_profile(db, current_user.id, req)
    return ResponseBase(data=result)


@router.put("/me/password", response_model=ResponseBase)
async def change_password_api(
    req: ChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await change_password(db, current_user.id, req)
    return ResponseBase(message="密码修改成功")


@router.get("/me/devices", response_model=PageResponse)
async def get_my_devices_api(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await get_my_devices(db, current_user.id, status, page, size)
    return PageResponse(data=result)


@router.get("/{user_id}/review-stats", response_model=ResponseBase)
async def get_review_stats_api(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await get_review_stats(db, user_id)
    return ResponseBase(data=result)
