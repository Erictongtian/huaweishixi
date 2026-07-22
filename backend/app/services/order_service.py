import math
import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BusinessException, ConflictException, NotFoundException, PermissionException
from app.models.device import Device, DeviceImage
from app.models.order import Order
from app.models.user import User
from app.schemas.order import (
    OrderCancel,
    OrderConfirm,
    OrderCreate,
    OrderListItem,
    OrderResponse,
)


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def create_order(db: AsyncSession, buyer_id: UUID, req: OrderCreate) -> OrderResponse:
    result = await db.execute(select(Device).where(Device.id == req.device_id))
    device = result.scalar_one_or_none()
    if device is None:
        raise NotFoundException("设备不存在")
    if device.seller_id == buyer_id:
        raise PermissionException("不能购买自己发布的设备")
    if device.status != "on_sale":
        raise BusinessException("该设备不在售")

    order_no = datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:6].upper()

    order = Order(
        order_no=order_no,
        device_id=req.device_id,
        buyer_id=buyer_id,
        seller_id=device.seller_id,
        price=device.price,
        buyer_message=req.buyer_message,
    )

    try:
        db.add(order)
        await db.flush()
    except Exception as e:
        if "idx_order_device_active" in str(e):
            raise ConflictException("该设备已有待处理的订单")
        raise

    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def confirm_order(db: AsyncSession, order_id: UUID, seller_id: UUID, req: OrderConfirm) -> OrderResponse:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundException("订单不存在")
    if order.seller_id != seller_id:
        raise PermissionException("只有卖家可以确认订单")
    if order.status != "pending":
        raise BusinessException("仅待确认订单可确认")

    order.status = "confirmed"
    order.seller_remark = req.seller_remark
    order.confirmed_at = _utcnow()
    await db.flush()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def reject_order(db: AsyncSession, order_id: UUID, seller_id: UUID) -> OrderResponse:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundException("订单不存在")
    if order.seller_id != seller_id:
        raise PermissionException("只有卖家可以拒绝订单")
    if order.status != "pending":
        raise BusinessException("仅待确认订单可拒绝")

    order.status = "cancelled"
    order.cancelled_at = _utcnow()
    order.cancel_reason = "卖家拒绝"
    await db.flush()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def complete_order(db: AsyncSession, order_id: UUID, buyer_id: UUID) -> OrderResponse:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundException("订单不存在")
    if order.buyer_id != buyer_id:
        raise PermissionException("只有买家可以确认交付")
    if order.status != "confirmed":
        raise BusinessException("仅已确认订单可确认交付")

    order.status = "completed"
    order.completed_at = _utcnow()
    await db.flush()

    device_result = await db.execute(select(Device).where(Device.id == order.device_id))
    device = device_result.scalar_one_or_none()
    if device:
        device.status = "sold"
        await db.flush()

    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def cancel_order(db: AsyncSession, order_id: UUID, user_id: UUID, req: OrderCancel) -> OrderResponse:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundException("订单不存在")
    if order.buyer_id != user_id and order.seller_id != user_id:
        raise PermissionException("只有买家或卖家可以取消订单")
    if order.status not in ("pending", "confirmed"):
        raise BusinessException("仅待确认/已确认订单可取消")

    order.status = "cancelled"
    order.cancelled_at = _utcnow()
    order.cancel_reason = req.cancel_reason
    await db.flush()
    await db.refresh(order)
    return OrderResponse.model_validate(order)


async def get_order_detail(db: AsyncSession, order_id: UUID, user_id: UUID) -> OrderResponse:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundException("订单不存在")
    if order.buyer_id != user_id and order.seller_id != user_id:
        raise PermissionException("无权查看该订单")

    device_result = await db.execute(
        select(Device).where(Device.id == order.device_id)
    )
    device = device_result.scalar_one_or_none()

    img_result = await db.execute(
        select(DeviceImage.url).where(DeviceImage.device_id == order.device_id).order_by(DeviceImage.sort_order).limit(1)
    )
    img_url = img_result.scalar()

    buyer_result = await db.execute(select(User).where(User.id == order.buyer_id))
    buyer = buyer_result.scalar_one_or_none()

    seller_result = await db.execute(select(User).where(User.id == order.seller_id))
    seller = seller_result.scalar_one_or_none()

    resp = OrderResponse.model_validate(order)
    if device:
        resp.device = {"id": device.id, "title": device.title, "price": device.price, "image_url": img_url}
    if buyer:
        resp.buyer = {"id": buyer.id, "username": buyer.username, "nickname": buyer.nickname}
    if seller:
        resp.seller = {"id": seller.id, "username": seller.username, "nickname": seller.nickname}
    return resp


async def get_my_orders(
    db: AsyncSession,
    user_id: UUID,
    role: str = "buyer",
    status: str | None = None,
    page: int = 1,
    size: int = 20,
) -> dict:
    conditions = []
    if role == "buyer":
        conditions.append(Order.buyer_id == user_id)
    else:
        conditions.append(Order.seller_id == user_id)
    if status:
        conditions.append(Order.status == status)

    where = and_(*conditions)

    count_result = await db.execute(select(func.count()).select_from(Order).where(where))
    total = count_result.scalar() or 0

    query = (
        select(Order)
        .where(where)
        .order_by(Order.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query)
    orders = result.scalars().all()

    items = []
    for o in orders:
        dev_result = await db.execute(select(Device.title).where(Device.id == o.device_id))
        dev_title = dev_result.scalar()

        img_result = await db.execute(
            select(DeviceImage.url).where(DeviceImage.device_id == o.device_id).order_by(DeviceImage.sort_order).limit(1)
        )
        img_url = img_result.scalar()

        items.append(OrderListItem(
            id=o.id,
            order_no=o.order_no,
            device_id=o.device_id,
            buyer_id=o.buyer_id,
            seller_id=o.seller_id,
            price=o.price,
            status=o.status,
            created_at=o.created_at,
            device_title=dev_title,
            device_image_url=img_url,
        ).model_dump())

    pages = math.ceil(total / size) if total > 0 else 0
    return {"items": items, "total": total, "page": page, "size": size, "pages": pages}