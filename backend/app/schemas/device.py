from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_validator


class ImageReorder(BaseModel):
    image_ids: list[UUID]

    @field_validator("image_ids")
    @classmethod
    def validate_image_ids(cls, v: list[UUID]) -> list[UUID]:
        if not v:
            raise ValueError("图片列表不能为空")
        return v


class DeviceCreate(BaseModel):
    title: str
    description: str
    category_id: UUID
    price: Decimal
    original_price: Decimal | None = None
    usage_duration: str | None = None
    condition_level: str
    location: str | None = None
    contact_info: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("标题不能为空")
        if len(v) > 100:
            raise ValueError("标题最长100个字符")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("设备描述不能为空")
        return v.strip()

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0 or v > 99999.99:
            raise ValueError("价格须在0.01-99999.99之间")
        return v

    @field_validator("condition_level")
    @classmethod
    def validate_condition(cls, v: str) -> str:
        if v not in ("almost_new", "good", "fair", "poor"):
            raise ValueError("成色须为almost_new/good/fair/poor")
        return v

    @field_validator("contact_info")
    @classmethod
    def validate_contact_info(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("联系方式不能为空")
        return v.strip()


class DeviceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category_id: UUID | None = None
    usage_duration: str | None = None
    condition_level: str | None = None
    location: str | None = None
    contact_info: str | None = None

    @field_validator("condition_level")
    @classmethod
    def validate_condition(cls, v: str | None) -> str | None:
        if v and v not in ("almost_new", "good", "fair", "poor"):
            raise ValueError("成色须为almost_new/good/fair/poor")
        return v


class PriceUpdate(BaseModel):
    price: Decimal

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0 or v > 99999.99:
            raise ValueError("价格须在0.01-99999.99之间")
        return v


class StatusUpdate(BaseModel):
    action: str

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ("on_sale", "off_shelf"):
            raise ValueError("操作须为on_sale或off_shelf")
        return v


class DeviceImageResponse(BaseModel):
    id: UUID
    url: str
    sort_order: int

    model_config = {"from_attributes": True}


class SellerBrief(BaseModel):
    id: UUID
    username: str
    nickname: str
    avatar: str | None = None

    model_config = {"from_attributes": True}


class CategoryBrief(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}


class DeviceResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    category_id: UUID
    price: Decimal
    original_price: Decimal | None = None
    usage_duration: str | None = None
    condition_level: str
    status: str
    seller_id: UUID
    view_count: int = 0
    location: str | None = None
    contact_info: str | None = None
    created_at: datetime
    updated_at: datetime
    images: list[DeviceImageResponse] = []
    category: CategoryBrief | None = None
    seller: SellerBrief | None = None

    model_config = {"from_attributes": True}


class DeviceListItem(BaseModel):
    id: UUID
    title: str
    price: Decimal
    original_price: Decimal | None = None
    condition_level: str
    status: str
    view_count: int = 0
    location: str | None = None
    created_at: datetime
    image_url: str | None = None
    category_name: str | None = None
    seller_nickname: str | None = None

    model_config = {"from_attributes": True}


class DeviceCreateResponse(BaseModel):
    id: UUID
    title: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DevicePriceResponse(BaseModel):
    id: UUID
    price: Decimal
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeviceStatusResponse(BaseModel):
    id: UUID
    status: str
    updated_at: datetime

    model_config = {"from_attributes": True}