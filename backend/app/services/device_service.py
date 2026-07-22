import math
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from app.core.exceptions import BusinessException, ConflictException, NotFoundException, PermissionException
from app.models.category import Category
from app.models.device import Device, DeviceImage
from app.models.order import Order
from app.models.user import User
from app.schemas.device import (
    DeviceCreate,
    DeviceCreateResponse,
    DeviceImageResponse,
    DeviceListItem,
    DevicePriceResponse,
    DeviceResponse,
    DeviceStatusResponse,
    DeviceUpdate,
    PriceUpdate,
    StatusUpdate,
)
from app.utils.file import save_upload_file, delete_file


async def get_devices(
    db: AsyncSession,
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    category: UUID | None = None,
    condition_level: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = "created_at",
    order: str = "desc",
) -> dict:
    conditions = [Device.status == "on_sale"]

    if keyword:
        conditions.append(or_(Device.title.ilike(f"%{keyword}%"), Device.description.ilike(f"%{keyword}%")))
    if category:
        conditions.append(Device.category_id == category)
    if condition_level:
        conditions.append(Device.condition_level == condition_level)
    if min_price is not None:
        conditions.append(Device.price >= min_price)
    if max_price is not None:
        conditions.append(Device.price <= max_price)

    where = and_(*conditions)

    count_result = await db.execute(select(func.count()).select_from(Device).where(where))
    total = count_result.scalar() or 0

    sort_col = getattr(Device, sort, Device.created_at)
    if order == "asc":
        sort_col = sort_col.asc()
    else:
        sort_col = sort_col.desc()

    query = (
        select(Device)
        .options(selectinload(Device.images))
        .where(where)
        .order_by(sort_col)
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query)
    devices = result.scalars().all()

    items = []
    for d in devices:
        cat_result = await db.execute(select(Category.name).where(Category.id == d.category_id))
        cat_name = cat_result.scalar()

        seller_result = await db.execute(select(User.nickname).where(User.id == d.seller_id))
        seller_nick = seller_result.scalar()

        image_url = d.images[0].url if d.images else None
        items.append(DeviceListItem(
            id=d.id,
            title=d.title,
            price=d.price,
            original_price=d.original_price,
            condition_level=d.condition_level,
            status=d.status,
            view_count=d.view_count,
            location=d.location,
            created_at=d.created_at,
            image_url=image_url,
            category_name=cat_name,
            seller_nickname=seller_nick,
        ))

    pages = math.ceil(total / size) if total > 0 else 0
    return {"items": [i.model_dump() for i in items], "total": total, "page": page, "size": size, "pages": pages}


async def create_device(db: AsyncSession, seller_id: UUID, req: DeviceCreate) -> DeviceCreateResponse:
    result = await db.execute(select(Category).where(Category.id == req.category_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundException("分类不存在")

    device = Device(
        title=req.title,
        description=req.description,
        category_id=req.category_id,
        price=req.price,
        original_price=req.original_price,
        usage_duration=req.usage_duration,
        condition_level=req.condition_level,
        location=req.location,
        contact_info=req.contact_info,
        seller_id=seller_id,
    )
    db.add(device)
    await db.flush()
    return DeviceCreateResponse.model_validate(device)


async def add_device_image(db: AsyncSession, device_id: UUID, seller_id: UUID, file) -> DeviceImageResponse:
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if device is None:
        raise NotFoundException("设备不存在")
    if device.seller_id != seller_id:
        raise PermissionException("只能上传自己设备的图片")

    count_result = await db.execute(
        select(func.count()).where(DeviceImage.device_id == device_id)
    )
    if count_result.scalar() >= 5:
        raise BusinessException("最多上传5张图片")

    file_info = await save_upload_file(file)

    max_order_result = await db.execute(
        select(func.max(DeviceImage.sort_order)).where(DeviceImage.device_id == device_id)
    )
    max_order = max_order_result.scalar() or 0

    image = DeviceImage(
        device_id=device_id,
        url=file_info["url"],
        sort_order=max_order + 1,
    )
    db.add(image)
    await db.flush()
    return DeviceImageResponse.model_validate(image)


async def delete_device_image(db: AsyncSession, device_id: UUID, image_id: UUID, seller_id: UUID) -> None:
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if device is None:
        raise NotFoundException("设备不存在")
    if device.seller_id != seller_id:
        raise PermissionException("只能删除自己设备的图片")

    img_result = await db.execute(
        select(DeviceImage).where(DeviceImage.id == image_id, DeviceImage.device_id == device_id)
    )
    image = img_result.scalar_one_or_none()
    if image is None:
        raise NotFoundException("图片不存在")

    delete_file(image.url)
    await db.delete(image)
    await db.flush()


async def reorder_device_images(db: AsyncSession, device_id: UUID, seller_id: UUID, image_ids: list) -> None:
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if device is None:
        raise NotFoundException("设备不存在")
    if device.seller_id != seller_id:
        raise PermissionException("只能操作自己设备的图片")

    for idx, image_id in enumerate(image_ids):
        img_result = await db.execute(
            select(DeviceImage).where(DeviceImage.id == image_id, DeviceImage.device_id == device_id)
        )
        image = img_result.scalar_one_or_none()
        if image:
            image.sort_order = idx
    await db.flush()


async def get_device_detail(db: AsyncSession, device_id: UUID) -> DeviceResponse:
    result = await db.execute(
        select(Device)
        .options(selectinload(Device.images))
        .where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    if device is None:
        raise NotFoundException("设备不存在")

    device.view_count += 1
    await db.flush()
    await db.refresh(device)

    cat_result = await db.execute(select(Category).where(Category.id == device.category_id))
    category = cat_result.scalar_one_or_none()

    seller_result = await db.execute(select(User).where(User.id == device.seller_id))
    seller = seller_result.scalar_one_or_none()

    resp = DeviceResponse.model_validate(device)
    if category:
        resp.category = {"id": category.id, "name": category.name}
    if seller:
        resp.seller = {"id": seller.id, "username": seller.username, "nickname": seller.nickname, "avatar": seller.avatar}
    return resp


async def update_device(db: AsyncSession, device_id: UUID, seller_id: UUID, req: DeviceUpdate) -> DeviceResponse:
    result = await db.execute(
        select(Device).options(selectinload(Device.images)).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    if device is None:
        raise NotFoundException("设备不存在")
    if device.seller_id != seller_id:
        raise PermissionException("只能修改自己的设备")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(device, key, value)
    await db.flush()
    await db.refresh(device, ["images"])

    cat_result = await db.execute(select(Category).where(Category.id == device.category_id))
    category = cat_result.scalar_one_or_none()
    seller_result = await db.execute(select(User).where(User.id == device.seller_id))
    seller = seller_result.scalar_one_or_none()

    resp = DeviceResponse.model_validate(device)
    if category:
        resp.category = {"id": category.id, "name": category.name}
    if seller:
        resp.seller = {"id": seller.id, "username": seller.username, "nickname": seller.nickname, "avatar": seller.avatar}
    return resp


async def update_price(db: AsyncSession, device_id: UUID, seller_id: UUID, req: PriceUpdate) -> DevicePriceResponse:
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if device is None:
        raise NotFoundException("设备不存在")
    if device.seller_id != seller_id:
        raise PermissionException("只能修改自己设备的价格")
    if device.status not in ("on_sale", "off_shelf"):
        raise BusinessException("仅在售/已下架状态可修改价格")

    device.price = req.price
    await db.flush()
    await db.refresh(device)
    return DevicePriceResponse.model_validate(device)


async def toggle_status(db: AsyncSession, device_id: UUID, seller_id: UUID, req: StatusUpdate) -> DeviceStatusResponse:
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if device is None:
        raise NotFoundException("设备不存在")
    if device.seller_id != seller_id:
        raise PermissionException("只能操作自己的设备")

    if req.action == "off_shelf":
        if device.status != "on_sale":
            raise BusinessException("仅在售设备可下架")
        active_orders = await db.execute(
            select(func.count()).where(
                and_(Order.device_id == device_id, Order.status.in_(["pending", "confirmed"]))
            )
        )
        if active_orders.scalar() > 0:
            raise ConflictException("存在待确认或已确认的订单，无法下架")
        device.status = "off_shelf"
    elif req.action == "on_sale":
        if device.status != "off_shelf":
            raise BusinessException("仅已下架设备可上架")
        device.status = "on_sale"

    await db.flush()
    await db.refresh(device)
    return DeviceStatusResponse.model_validate(device)


async def delete_device(db: AsyncSession, device_id: UUID, seller_id: UUID) -> None:
    result = await db.execute(
        select(Device).options(selectinload(Device.images)).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    if device is None:
        raise NotFoundException("设备不存在")
    if device.seller_id != seller_id:
        raise PermissionException("只能删除自己的设备")
    if device.status != "off_shelf":
        raise BusinessException("仅已下架设备可删除")

    for image in device.images:
        delete_file(image.url)

    await db.delete(device)
    await db.flush()