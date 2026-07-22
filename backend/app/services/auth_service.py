from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import BusinessException, ConflictException, NotFoundException, PermissionException
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


async def register(db: AsyncSession, req: RegisterRequest) -> UserResponse:
    result = await db.execute(select(User).where(User.username == req.username))
    if result.scalar_one_or_none():
        raise ConflictException("用户名已存在")

    if req.email:
        result = await db.execute(select(User).where(User.email == req.email))
        if result.scalar_one_or_none():
            raise ConflictException("邮箱已被注册")

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        nickname=req.nickname,
        email=req.email,
        phone=req.phone,
    )
    db.add(user)
    await db.flush()
    return UserResponse.model_validate(user)


async def authenticate(db: AsyncSession, req: LoginRequest) -> TokenResponse:
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if user is None:
        raise BusinessException("用户名或密码错误", code=401)

    now = datetime.utcnow()

    if user.status == "disabled":
        raise PermissionException("账号已注销")

    if user.status == "locked" and user.locked_until is None:
        raise PermissionException("账号已被封禁")

    if user.status == "locked" and user.locked_until and user.locked_until > now:
        remaining = int((user.locked_until - now).total_seconds() / 60)
        raise PermissionException(f"账号已锁定，请{remaining}分钟后再试")

    if user.status == "locked" and user.locked_until and user.locked_until <= now:
        user.status = "active"
        user.fail_count = 0
        user.locked_until = None

    if not verify_password(req.password, user.password_hash):
        user.fail_count += 1
        if user.fail_count >= 5:
            user.status = "locked"
            user.locked_until = now + timedelta(minutes=30)
            await db.commit()
            raise PermissionException("密码错误次数过多，账号已锁定30分钟")
        await db.commit()
        raise BusinessException("用户名或密码错误", code=401)

    user.fail_count = 0
    user.locked_until = None
    user.status = "active"
    user.last_login_at = now
    await db.flush()

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE,
        user=UserResponse.model_validate(user),
    )


async def refresh_access_token(refresh_token_str: str) -> RefreshTokenResponse:
    try:
        payload = decode_token(refresh_token_str)
    except ValueError:
        raise BusinessException("无效的刷新令牌", code=401)

    if payload.get("type") != "refresh":
        raise BusinessException("无效的令牌类型", code=401)

    user_id = payload.get("sub")
    role = payload.get("role", "user")

    access_token = create_access_token(data={"sub": user_id, "role": role})
    return RefreshTokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE,
    )


async def get_current_user_info(db: AsyncSession, user_id: str) -> UserResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("用户不存在")
    return UserResponse.model_validate(user)