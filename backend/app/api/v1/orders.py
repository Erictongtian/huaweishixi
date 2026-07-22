from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.base import ResponseBase, PageResponse
from app.schemas.order import OrderCreate, OrderConfirm, OrderCancel
from app.services.order_service import (
    cancel_order,
    complete_order,
    confirm_order,
    create_order,
    get_my_orders,
    get_order_detail,
    reject_order,
)

router = APIRouter()


@router.post("", response_model=ResponseBase, status_code=201)
async def create_order_api(
    req: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await create_order(db, current_user.id, req)
    return ResponseBase(data=result)


@router.get("", response_model=PageResponse)
async def list_my_orders(
    role: str = Query("buyer"),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await get_my_orders(db, current_user.id, role, status, page, size)
    return PageResponse(data=result)


@router.get("/{order_id}", response_model=ResponseBase)
async def get_order_detail_api(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await get_order_detail(db, order_id, current_user.id)
    return ResponseBase(data=result)


@router.patch("/{order_id}/confirm", response_model=ResponseBase)
async def confirm_order_api(
    order_id: UUID,
    req: OrderConfirm,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await confirm_order(db, order_id, current_user.id, req)
    return ResponseBase(data=result)


@router.patch("/{order_id}/reject", response_model=ResponseBase)
async def reject_order_api(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await reject_order(db, order_id, current_user.id)
    return ResponseBase(data=result)


@router.patch("/{order_id}/complete", response_model=ResponseBase)
async def complete_order_api(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await complete_order(db, order_id, current_user.id)
    return ResponseBase(data=result)


@router.patch("/{order_id}/cancel", response_model=ResponseBase)
async def cancel_order_api(
    order_id: UUID,
    req: OrderCancel,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await cancel_order(db, order_id, current_user.id, req)
    return ResponseBase(data=result)
