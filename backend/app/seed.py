import asyncio
import uuid

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import User
from app.models.category import Category

CATEGORIES = [
    {"name": "暖壶", "icon": "thermos", "sort_order": 1},
    {"name": "电水壶", "icon": "kettle", "sort_order": 2},
    {"name": "电扇", "icon": "fan", "sort_order": 3},
    {"name": "微波炉", "icon": "microwave", "sort_order": 4},
    {"name": "移动硬盘", "icon": "hard-drive", "sort_order": 5},
    {"name": "其他", "icon": "other", "sort_order": 6},
]


async def seed():
    async with async_session_factory() as session:
        result = await session.execute(select(Category).limit(1))
        if result.scalar_one_or_none():
            print("Seed data already exists, skipping.")
            return

        for cat_data in CATEGORIES:
            category = Category(
                id=uuid.uuid4(),
                name=cat_data["name"],
                icon=cat_data["icon"],
                sort_order=cat_data["sort_order"],
                status="active",
            )
            session.add(category)

        admin = User(
            id=uuid.uuid4(),
            username="admin",
            password_hash=hash_password("Admin123456"),
            nickname="系统管理员",
            role="admin",
            status="active",
            fail_count=0,
        )
        session.add(admin)

        await session.commit()
        print(f"Inserted {len(CATEGORIES)} categories and 1 admin account.")


if __name__ == "__main__":
    asyncio.run(seed())