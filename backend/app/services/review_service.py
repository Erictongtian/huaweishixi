import math
from uuid import UUID

from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, ConflictException, NotFoundException, PermissionException
from app.models.order import Order
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewStatsResponse


async def create_review(db: AsyncSession, reviewer_id: UUID, req: ReviewCreate) -> ReviewResponse:
    result = await db.execute(select(Order).where(Order.id == req.order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundException("订单不存在")
    if order.buyer_id != reviewer_id:
        raise PermissionException("只有买家可以评价订单")
    if order.status != "completed":
        raise BusinessException("仅已完成的订单可评价")

    existing = await db.execute(
        select(Review).where(Review.order_id == req.order_id)
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictException("该订单已评价")

    review = Review(
        order_id=req.order_id,
        device_id=order.device_id,
        reviewer_id=reviewer_id,
        rating=req.rating,
        content=req.content,
        images=req.images,
    )
    db.add(review)
    await db.flush()
    await db.refresh(review)

    resp = ReviewResponse.model_validate(review)

    user_result = await db.execute(select(User).where(User.id == reviewer_id))
    user = user_result.scalar_one_or_none()
    if user:
        resp.reviewer_nickname = user.nickname
        resp.reviewer_avatar = user.avatar

    return resp


async def get_device_reviews(
    db: AsyncSession,
    device_id: UUID,
    page: int = 1,
    size: int = 20,
) -> dict:
    device_check = await db.execute(
        select(func.count()).select_from(Review).where(Review.device_id == device_id)
    )
    total = device_check.scalar() or 0

    query = (
        select(Review)
        .where(Review.device_id == device_id)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await db.execute(query)
    reviews = result.scalars().all()

    items = []
    for r in reviews:
        resp = ReviewResponse.model_validate(r)
        user_result = await db.execute(select(User).where(User.id == r.reviewer_id))
        user = user_result.scalar_one_or_none()
        if user:
            resp.reviewer_nickname = user.nickname
            resp.reviewer_avatar = user.avatar
        items.append(resp.model_dump())

    pages = math.ceil(total / size) if total > 0 else 0
    return {"items": items, "total": total, "page": page, "size": size, "pages": pages}


async def get_review_stats(db: AsyncSession, user_id: UUID) -> ReviewStatsResponse:
    user_result = await db.execute(select(User).where(User.id == user_id))
    if user_result.scalar_one_or_none() is None:
        raise NotFoundException("用户不存在")

    device_ids_subq = (
        select(Order.device_id)
        .where(Order.seller_id == user_id, Order.status == "completed")
        .subquery()
    )

    review_ids_subq = (
        select(Review.id)
        .where(Review.device_id.in_(select(device_ids_subq.c.device_id)))
        .subquery()
    )

    avg_result = await db.execute(
        select(func.avg(Review.rating)).where(Review.device_id.in_(select(device_ids_subq.c.device_id)))
    )
    avg_rating = avg_result.scalar() or 0.0

    count_result = await db.execute(
        select(func.count()).select_from(Review).where(Review.device_id.in_(select(device_ids_subq.c.device_id)))
    )
    total_reviews = count_result.scalar() or 0

    dist_result = await db.execute(
        select(
            Review.rating,
            func.count().label("cnt"),
        )
        .where(Review.device_id.in_(select(device_ids_subq.c.device_id)))
        .group_by(Review.rating)
    )
    distribution = {str(i): 0 for i in range(1, 6)}
    for row in dist_result:
        distribution[str(row.rating)] = row.cnt

    return ReviewStatsResponse(
        avg_rating=round(avg_rating, 1),
        total_reviews=total_reviews,
        rating_distribution=distribution,
    )