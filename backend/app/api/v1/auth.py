from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.base import ResponseBase
from app.services.auth_service import (
    authenticate,
    get_current_user_info,
    refresh_access_token,
    register,
)

router = APIRouter()
security_scheme = HTTPBearer()


@router.post("/register", response_model=ResponseBase[UserResponse], status_code=201)
async def register_user(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register(db, req)
    return ResponseBase(data=user)


@router.post("/login", response_model=ResponseBase[TokenResponse])
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    token_data = await authenticate(db, req)
    return ResponseBase(data=token_data)


@router.post("/refresh", response_model=ResponseBase[RefreshTokenResponse])
async def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
):
    token_data = await refresh_access_token(credentials.credentials)
    return ResponseBase(data=token_data)


@router.get("/me", response_model=ResponseBase[UserResponse])
async def get_me(current_user: User = Depends(get_current_user)):
    return ResponseBase(data=UserResponse.model_validate(current_user))
