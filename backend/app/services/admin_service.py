import math
from uuid import UUID

from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, NotFoundException, PermissionException
from app.core.security import hash_password
from app.models.device import Device
from app.models.order import Order
from app.models.user import User


async def list_users(
    db: AsyncSession,
    keyword: str | None = None,
    status: str | None = None,
    role: str | None = None,
    page: int = 1,
    size: int = 20,
) -> dict:
    conditions = []
    if keyword:
        conditions.append((User.username.ilike(f"%{keyword}%")) | (User.nickname.ilike(f"%{keyword}%")))
    if status:
        conditions.append(User.status == status)
    if role:
        conditions.append(User.role == role)

    where = and_(*conditions) if conditions else True

    count_result = await db.execute(select(func.count()).select_from(User).where(where))
    total = count_result.scalar() or 0

    query = (
        select(User)
        .where(where)
        .order_by(User.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query)
    users = result.scalars().all()

    items = []
    for u in users:
        items.append({
            "id": str(u.id),
            "username": u.username,
            "nickname": u.nickname,
            "email": u.email,
            "phone": u.phone,
            "avatar": u.avatar,
            "role": u.role,
            "status": u.status,
            "is_verified": u.is_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })

    pages = math.ceil(total / size) if total > 0 else 0
    return {"items": items, "total": total, "page": page, "size": size, "pages": pages}


async def ban_user(db: AsyncSession, user_id: UUID, admin_id: UUID) -> None:
    if user_id == admin_id:
        raise BusinessException("不能封禁自己")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("用户不存在")
    if user.role == "admin":
        raise BusinessException("不能封禁管理员")
    if user.status == "disabled":
        raise BusinessException("该账户已注销")
    user.status = "locked"
    user.locked_until = None
    await db.flush()


async def unban_user(db: AsyncSession, user_id: UUID, admin_id: UUID) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("用户不存在")
    if user.status != "locked":
        raise BusinessException("该用户未被封禁")
    user.status = "active"
    user.fail_count = 0
    user.locked_until = None
    await db.flush()


async def delete_user(db: AsyncSession, user_id: UUID, admin_id: UUID) -> None:
    if user_id == admin_id:
        raise BusinessException("不能注销自己")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("用户不存在")
    if user.role == "admin":
        raise BusinessException("不能注销管理员")
    if user.status == "disabled":
        raise BusinessException("该账户已注销")

    await db.execute(
        update(Device).where(Device.seller_id == user_id, Device.status == "on_sale")
        .values(status="off_shelf")
    )

    await db.execute(
        update(Order).where(
            (Order.buyer_id == user_id) | (Order.seller_id == user_id),
            Order.status.in_(["pending", "confirmed"]),
        ).values(status="cancelled", cancel_reason="账户已注销")
    )

    user.status = "disabled"
    await db.flush()


async def reset_user_password(db: AsyncSession, user_id: UUID, new_password: str) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("用户不存在")
    user.password_hash = hash_password(new_password)
    user.fail_count = 0
    user.locked_until = None
    if user.status == "locked":
        user.status = "active"
    await db.flush()