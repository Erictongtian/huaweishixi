from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.base import ResponseBase, PageResponse
from app.schemas.user import AdminResetPassword
from app.services.admin_service import list_users, ban_user, unban_user, delete_user, reset_user_password

router = APIRouter()


@router.get("/users", response_model=PageResponse)
async def list_users_api(
    keyword: str | None = Query(None),
    status: str | None = Query(None),
    role: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await list_users(db, keyword, status, role, page, size)
    return PageResponse(data=result)


@router.patch("/users/{user_id}/ban", response_model=ResponseBase)
async def ban_user_api(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await ban_user(db, user_id, current_user.id)
    return ResponseBase(message="用户已封禁")


@router.patch("/users/{user_id}/unban", response_model=ResponseBase)
async def unban_user_api(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await unban_user(db, user_id, current_user.id)
    return ResponseBase(message="用户已解封")


@router.delete("/users/{user_id}", status_code=204)
async def delete_user_api(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await delete_user(db, user_id, current_user.id)


@router.put("/users/{user_id}/password", response_model=ResponseBase)
async def reset_user_password_api(
    user_id: UUID,
    req: AdminResetPassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await reset_user_password(db, user_id, req.new_password)
    return ResponseBase(message="密码重置成功")