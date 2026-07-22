from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    order_id: UUID
    rating: int
    content: str | None = None
    images: list[str] | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("评分须为1-5")
        return v


class ReviewResponse(BaseModel):
    id: UUID
    order_id: UUID
    device_id: UUID
    reviewer_id: UUID
    rating: int
    content: str | None = None
    images: list[str] | None = None
    created_at: datetime
    updated_at: datetime
    reviewer_nickname: str | None = None
    reviewer_avatar: str | None = None

    model_config = {"from_attributes": True}


class ReviewStatsResponse(BaseModel):
    avg_rating: float
    total_reviews: int
    rating_distribution: dict[str, int]