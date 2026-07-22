import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.core.database import async_session_factory
from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.category import Category
from app.models.device import Device
from app.models.order import Order

import uuid as _uuid


@pytest_asyncio.fixture
async def setup_data():
    results = {}

    async with async_session_factory() as db:
        cat_result = await db.execute(select(Category).limit(1))
        cat = cat_result.scalar_one_or_none()
        cat_id = cat.id if cat else str(_uuid.uuid4())

        uid1 = str(_uuid.uuid4())
        buyer = User(
            id=uid1, username=f"rvb_{uid1[:8]}", password_hash=hash_password("Test123456"),
            nickname="买家", role="user", status="active",
        )
        uid2 = str(_uuid.uuid4())
        seller = User(
            id=uid2, username=f"rvs_{uid2[:8]}", password_hash=hash_password("Test123456"),
            nickname="卖家", role="user", status="active",
        )
        db.add_all([buyer, seller])
        await db.flush()

        did = str(_uuid.uuid4())
        device = Device(
            id=did, title="测试设备_评价", category_id=cat_id, seller_id=seller.id,
            price=100.00, condition_level="9成新", status="sold",
        )
        db.add(device)
        await db.flush()

        oid = str(_uuid.uuid4())
        order = Order(
            id=oid, order_no="ORD" + _uuid.uuid4().hex[:10].upper(),
            device_id=device.id, buyer_id=buyer.id, seller_id=seller.id,
            price=100.00, status="completed",
        )
        db.add(order)
        await db.flush()

        oid2 = str(_uuid.uuid4())
        order2 = Order(
            id=oid2, order_no="ORD" + _uuid.uuid4().hex[:10].upper(),
            device_id=device.id, buyer_id=buyer.id, seller_id=seller.id,
            price=100.00, status="confirmed",
        )
        db.add(order2)
        await db.commit()

    results["buyer"] = buyer
    results["seller"] = seller
    results["device"] = device
    results["order"] = order
    results["order2"] = order2
    results["buyer_token"] = create_access_token({"sub": str(buyer.id)})
    results["seller_token"] = create_access_token({"sub": str(seller.id)})
    yield results


@pytest.mark.asyncio(loop_scope="session")
async def test_create_review_success(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/reviews",
            json={"order_id": str(setup_data["order"].id), "rating": 5, "content": "非常好"},
            headers={"Authorization": f"Bearer {setup_data['buyer_token']}"},
        )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["rating"] == 5
    assert data["content"] == "非常好"
    assert data["reviewer_id"] == str(setup_data["buyer"].id)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_review_duplicate(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.post(
            "/api/v1/reviews",
            json={"order_id": str(setup_data["order"].id), "rating": 4},
            headers={"Authorization": f"Bearer {setup_data['buyer_token']}"},
        )
        assert r1.status_code == 201

        r2 = await client.post(
            "/api/v1/reviews",
            json={"order_id": str(setup_data["order"].id), "rating": 3},
            headers={"Authorization": f"Bearer {setup_data['buyer_token']}"},
        )
    assert r2.status_code == 409


@pytest.mark.asyncio(loop_scope="session")
async def test_create_review_non_buyer(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/reviews",
            json={"order_id": str(setup_data["order"].id), "rating": 5},
            headers={"Authorization": f"Bearer {setup_data['seller_token']}"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_create_review_incomplete_order(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/reviews",
            json={"order_id": str(setup_data["order2"].id), "rating": 5},
            headers={"Authorization": f"Bearer {setup_data['buyer_token']}"},
        )
    assert resp.status_code == 400


@pytest.mark.asyncio(loop_scope="session")
async def test_get_device_reviews(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/v1/reviews",
            json={"order_id": str(setup_data["order"].id), "rating": 4, "content": "不错"},
            headers={"Authorization": f"Bearer {setup_data['buyer_token']}"},
        )
        resp = await client.get(f"/api/v1/devices/{setup_data['device'].id}/reviews")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_get_review_stats(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/v1/reviews",
            json={"order_id": str(setup_data["order"].id), "rating": 5},
            headers={"Authorization": f"Bearer {setup_data['buyer_token']}"},
        )
        resp = await client.get(f"/api/v1/users/{setup_data['seller'].id}/review-stats")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "avg_rating" in data
    assert "total_reviews" in data
    assert "rating_distribution" in data
