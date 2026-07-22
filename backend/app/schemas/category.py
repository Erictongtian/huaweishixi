from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    icon: str | None = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    sort_order: int | None = None


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    icon: str | None = None
    sort_order: int
    status: str
    device_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}