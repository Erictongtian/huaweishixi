import math

from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1, description="页码")
    size: int = Query(20, ge=1, le=100, description="每页数量")


def calc_pages(total: int, size: int) -> int:
    if total == 0:
        return 0
    return math.ceil(total / size)