from datetime import datetime
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import PermissionException
from app.core.security import decode_token
from app.models.user import User

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
) -> User:
    try:
        payload = decode_token(credentials.credentials)
    except ValueError:
        raise PermissionException("无效或过期的令牌")

    if payload.get("type") != "access":
        raise PermissionException("无效的令牌类型")

    user_id = payload.get("sub")
    if user_id is None:
        raise PermissionException("无效的令牌载荷")

    from app.core.database import get_db

    async for db in get_db():
        from sqlalchemy import select

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise PermissionException("用户不存在")

        now = datetime.utcnow()
        if user.status == "locked":
            if user.locked_until is None:
                raise PermissionException("账号已被封禁")
            if user.locked_until > now:
                raise PermissionException("账号已锁定")
            user.status = "active"
            user.fail_count = 0
            user.locked_until = None
            await db.flush()

        if user.status == "disabled":
            raise PermissionException("账号已注销")

        return user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != "admin":
        raise PermissionException("需要管理员权限")
    return current_user
