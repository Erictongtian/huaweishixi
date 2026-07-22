from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.base import ResponseBase
from app.schemas.review import ReviewCreate
from app.services.review_service import create_review

router = APIRouter()


@router.post("", response_model=ResponseBase, status_code=201)
async def create_review_api(
    req: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await create_review(db, current_user.id, req)
    return ResponseBase(data=result)
