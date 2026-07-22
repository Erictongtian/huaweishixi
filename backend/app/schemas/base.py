from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class FieldError(BaseModel):
    field: str
    message: str


class ResponseBase(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T | None = None


class PageData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class PageResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: PageData[T]


class ErrorResponse(BaseModel):
    code: int
    message: str
    errors: list[FieldError] = []