import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: str
    email: str
    email_code: str
    phone: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]{3,20}$", v):
            raise ValueError("用户名须3-20位，仅含字母、数字、下划线")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 20:
            raise ValueError("密码须8-20位")
        if not re.search(r"[a-zA-Z]", v) or not re.search(r"\d", v):
            raise ValueError("密码须包含字母和数字")
        return v

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("昵称不能为空")
        if len(v) > 50:
            raise ValueError("昵称最长50个字符")
        return v.strip()

    @field_validator("email_code")
    @classmethod
    def validate_email_code(cls, v: str) -> str:
        if not v or len(v) != 6:
            raise ValueError("验证码为6位数字")
        return v


class SendCodeRequest(BaseModel):
    email: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    nickname: str
    email: str | None = None
    phone: str | None = None
    role: str
    avatar: str | None = None
    is_verified: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    message: str
    email: str


class VerifyResponse(BaseModel):
    message: str



class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int