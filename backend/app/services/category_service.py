from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException, ConflictException, NotFoundException
from app.models.category import Category
from app.models.device import Device
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse


async def get_categories(db: AsyncSession) -> list[CategoryResponse]:
    result = await db.execute(
        select(Category).where(Category.status == "active").order_by(Category.sort_order)
    )
    categories = result.scalars().all()

    count_result = await db.execute(
        select(Device.category_id, func.count().label("cnt"))
        .where(Device.category_id.in_([c.id for c in categories]))
        .where(Device.status == "on_sale")
        .group_by(Device.category_id)
    )
    count_map = {row.category_id: row.cnt for row in count_result}

    items = []
    for c in categories:
        resp = CategoryResponse.model_validate(c)
        resp.device_count = count_map.get(c.id, 0)
        items.append(resp)
    return items


async def create_category(db: AsyncSession, req: CategoryCreate) -> CategoryResponse:
    existing = await db.execute(
        select(Category).where(Category.name == req.name)
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictException("分类名称已存在")

    category = Category(
        name=req.name,
        icon=req.icon,
        sort_order=req.sort_order,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)


async def update_category(db: AsyncSession, category_id: UUID, req: CategoryUpdate) -> CategoryResponse:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise NotFoundException("分类不存在")

    if req.name is not None:
        existing = await db.execute(
            select(Category).where(Category.name == req.name, Category.id != category_id)
        )
        if existing.scalar_one_or_none() is not None:
            raise ConflictException("分类名称已存在")
        category.name = req.name
    if req.icon is not None:
        category.icon = req.icon
    if req.sort_order is not None:
        category.sort_order = req.sort_order

    await db.flush()
    await db.refresh(category)
    return CategoryResponse.model_validate(category)


async def delete_category(db: AsyncSession, category_id: UUID) -> None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise NotFoundException("分类不存在")

    device_count = await db.execute(
        select(func.count()).select_from(Device).where(Device.category_id == category_id)
    )
    if (device_count.scalar() or 0) > 0:
        raise BusinessException("该分类下存在设备，无法删除")

    await db.delete(category)
    await db.flush()