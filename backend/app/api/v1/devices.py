from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.base import ResponseBase, PageResponse
from app.schemas.device import DeviceCreate, DeviceUpdate, PriceUpdate, StatusUpdate, ImageReorder
from app.services.device_service import (
    add_device_image,
    create_device,
    delete_device,
    delete_device_image,
    get_device_detail,
    get_devices,
    reorder_device_images,
    toggle_status,
    update_device,
    update_price,
)
from app.services.review_service import get_device_reviews

router = APIRouter()


@router.get("", response_model=PageResponse)
async def list_devices(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    category: UUID | None = Query(None),
    condition_level: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
):
    result = await get_devices(db, page, size, keyword, category, condition_level, min_price, max_price, sort, order)
    return PageResponse(data=result)


@router.post("", response_model=ResponseBase, status_code=201)
async def create_device_api(
    title: str = Form(...),
    category_id: UUID = Form(...),
    price: str = Form(...),
    condition_level: str = Form(...),
    description: str = Form(...),
    original_price: str | None = Form(None),
    usage_duration: str | None = Form(None),
    location: str | None = Form(None),
    contact_info: str = Form(...),
    images: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from decimal import Decimal

    if not images or len(images) == 0:
        from ..core.exceptions import ValidationException
        raise ValidationException("请至少上传一张设备照片")

    req = DeviceCreate(
        title=title,
        description=description,
        category_id=category_id,
        price=Decimal(price),
        original_price=Decimal(original_price) if original_price else None,
        usage_duration=usage_duration,
        condition_level=condition_level,
        location=location,
        contact_info=contact_info,
    )
    result = await create_device(db, current_user.id, req)
    for img in images[:5]:
        await add_device_image(db, result.id, current_user.id, img)
    return ResponseBase(data=result)


@router.get("/{device_id}", response_model=ResponseBase)
async def get_device_detail_api(device_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await get_device_detail(db, device_id)
    return ResponseBase(data=result)


@router.put("/{device_id}", response_model=ResponseBase)
async def update_device_api(
    device_id: UUID,
    req: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await update_device(db, device_id, current_user.id, req)
    return ResponseBase(data=result)


@router.patch("/{device_id}/price", response_model=ResponseBase)
async def update_price_api(
    device_id: UUID,
    req: PriceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await update_price(db, device_id, current_user.id, req)
    return ResponseBase(data=result)


@router.patch("/{device_id}/status", response_model=ResponseBase)
async def toggle_status_api(
    device_id: UUID,
    req: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await toggle_status(db, device_id, current_user.id, req)
    return ResponseBase(data=result)


@router.delete("/{device_id}", status_code=204)
async def delete_device_api(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await delete_device(db, device_id, current_user.id)


@router.post("/{device_id}/images", response_model=ResponseBase, status_code=201)
async def upload_device_image(
    device_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await add_device_image(db, device_id, current_user.id, file)
    return ResponseBase(data=result)


@router.delete("/{device_id}/images/{image_id}", status_code=204)
async def delete_device_image_api(
    device_id: UUID,
    image_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await delete_device_image(db, device_id, image_id, current_user.id)


@router.put("/{device_id}/images/reorder", response_model=ResponseBase)
async def reorder_device_images_api(
    device_id: UUID,
    req: ImageReorder,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await reorder_device_images(db, device_id, current_user.id, req.image_ids)
    return ResponseBase(data={"reordered": len(req.image_ids)})


@router.get("/{device_id}/reviews", response_model=PageResponse)
async def get_device_reviews_api(
    device_id: UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await get_device_reviews(db, device_id, page, size)
    return PageResponse(data=result)
