from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.base import ResponseBase
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category_service import get_categories, create_category, update_category, delete_category

router = APIRouter()


@router.get("", response_model=ResponseBase)
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await get_categories(db)
    return ResponseBase(data=result)


@router.post("", response_model=ResponseBase, status_code=201)
async def create_category_api(
    req: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await create_category(db, req)
    return ResponseBase(data=result)


@router.put("/{category_id}", response_model=ResponseBase)
async def update_category_api(
    category_id: UUID,
    req: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await update_category(db, category_id, req)
    return ResponseBase(data=result)


@router.delete("/{category_id}", status_code=204)
async def delete_category_api(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    await delete_category(db, category_id)
