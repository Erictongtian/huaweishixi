from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class OrderCreate(BaseModel):
    device_id: UUID
    buyer_message: str | None = None


class OrderConfirm(BaseModel):
    seller_remark: str | None = None


class OrderCancel(BaseModel):
    cancel_reason: str

    @field_validator("cancel_reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("取消原因不能为空")
        return v.strip()


class DeviceBrief(BaseModel):
    id: UUID
    title: str
    price: float
    image_url: str | None = None

    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    id: UUID
    username: str
    nickname: str

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: UUID
    order_no: str
    device_id: UUID
    buyer_id: UUID
    seller_id: UUID
    price: float
    status: str
    buyer_message: str | None = None
    seller_remark: str | None = None
    confirmed_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    cancel_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    device: DeviceBrief | None = None
    buyer: UserBrief | None = None
    seller: UserBrief | None = None

    model_config = {"from_attributes": True}


class OrderListItem(BaseModel):
    id: UUID
    order_no: str
    device_id: UUID
    buyer_id: UUID
    seller_id: UUID
    price: float
    status: str
    created_at: datetime
    device_title: str | None = None
    device_image_url: str | None = None

    model_config = {"from_attributes": True}