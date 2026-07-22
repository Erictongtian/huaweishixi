import math
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, ConflictException, NotFoundException, PermissionException
from app.core.security import verify_password, hash_password
from app.models.device import Device, DeviceImage
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import ProfileUpdate, ChangePassword


async def update_profile(db: AsyncSession, user_id: UUID, req: ProfileUpdate) -> UserResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("用户不存在")

    if req.email is not None and req.email != user.email:
        existing = await db.execute(select(User).where(User.email == req.email, User.id != user_id))
        if existing.scalar_one_or_none():
            raise ConflictException("邮箱已被使用")
        user.email = req.email

    if req.nickname is not None:
        user.nickname = req.nickname
    if req.phone is not None:
        user.phone = req.phone
    if req.avatar is not None:
        user.avatar = req.avatar

    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


async def change_password(db: AsyncSession, user_id: UUID, req: ChangePassword) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("用户不存在")

    if not verify_password(req.old_password, user.password_hash):
        raise PermissionException("旧密码错误")

    user.password_hash = hash_password(req.new_password)
    await db.flush()


async def get_my_devices(
    db: AsyncSession,
    user_id: UUID,
    status: str | None = None,
    page: int = 1,
    size: int = 20,
) -> dict:
    conditions = [Device.seller_id == user_id]
    if status:
        conditions.append(Device.status == status)

    where = and_(*conditions)

    count_result = await db.execute(select(func.count()).select_from(Device).where(where))
    total = count_result.scalar() or 0

    query = (
        select(Device)
        .where(where)
        .order_by(Device.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query)
    devices = result.scalars().all()

    items = []
    for d in devices:
        img_result = await db.execute(
            select(DeviceImage.url).where(DeviceImage.device_id == d.id)
            .order_by(DeviceImage.sort_order).limit(1)
        )
        img_url = img_result.scalar()

        items.append({
            "id": str(d.id),
            "title": d.title,
            "price": float(d.price),
            "original_price": float(d.original_price) if d.original_price else None,
            "condition_level": d.condition_level,
            "status": d.status,
            "view_count": d.view_count,
            "location": d.location,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "image_url": img_url,
            "category_id": str(d.category_id),
        })

    pages = math.ceil(total / size) if total > 0 else 0
    return {"items": items, "total": total, "page": page, "size": size, "pages": pages}