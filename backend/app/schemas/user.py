from pydantic import BaseModel, field_validator

import re


class ProfileUpdate(BaseModel):
    nickname: str | None = None
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("昵称不能为空")
            if len(v) > 50:
                raise ValueError("昵称最长50个字符")
        return v


class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 20:
            raise ValueError("密码须8-20位")
        if not re.search(r"[a-zA-Z]", v) or not re.search(r"\d", v):
            raise ValueError("密码须包含字母和数字")
        return v


class AdminResetPassword(BaseModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 20:
            raise ValueError("密码须8-20位")
        if not re.search(r"[a-zA-Z]", v) or not re.search(r"\d", v):
            raise ValueError("密码须包含字母和数字")
        return v


class AdminUserItem(BaseModel):
    id: str
    username: str
    nickname: str
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    role: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}