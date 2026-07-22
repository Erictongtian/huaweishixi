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

import uuid as _uuid


@pytest_asyncio.fixture
async def setup_data():
    results = {}

    async with async_session_factory() as db:
        uid = str(_uuid.uuid4())
        admin = User(
            id=uid, username=f"cat_admin_{uid[:8]}", password_hash=hash_password("Test123456"),
            nickname="管理员", role="admin", status="active",
        )
        uid2 = str(_uuid.uuid4())
        normal_user = User(
            id=uid2, username=f"cat_user_{uid2[:8]}", password_hash=hash_password("Test123456"),
            nickname="普通用户", role="user", status="active",
        )
        db.add_all([admin, normal_user])
        await db.commit()

    results["admin"] = admin
    results["admin_token"] = create_access_token({"sub": str(admin.id)})
    results["user"] = normal_user
    results["user_token"] = create_access_token({"sub": str(normal_user.id)})
    yield results


@pytest.mark.asyncio(loop_scope="session")
async def test_list_categories(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/categories")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "device_count" in data[0]


@pytest.mark.asyncio(loop_scope="session")
async def test_create_category(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/categories",
            json={"name": "测试分类_" + _uuid.uuid4().hex[:6], "sort_order": 10},
            headers={"Authorization": f"Bearer {setup_data['admin_token']}"},
        )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"].startswith("测试分类_")
    assert data["sort_order"] == 10


@pytest.mark.asyncio(loop_scope="session")
async def test_create_category_duplicate(setup_data):
    cat_name = "dup_cat_" + _uuid.uuid4().hex[:6]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/v1/categories",
            json={"name": cat_name},
            headers={"Authorization": f"Bearer {setup_data['admin_token']}"},
        )
        resp = await client.post(
            "/api/v1/categories",
            json={"name": cat_name},
            headers={"Authorization": f"Bearer {setup_data['admin_token']}"},
        )
    assert resp.status_code == 409


@pytest.mark.asyncio(loop_scope="session")
async def test_create_category_non_admin(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/categories",
            json={"name": "非管理员分类"},
            headers={"Authorization": f"Bearer {setup_data['user_token']}"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_update_category(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/categories",
            json={"name": "更新前_" + _uuid.uuid4().hex[:6]},
            headers={"Authorization": f"Bearer {setup_data['admin_token']}"},
        )
        cat_id = create_resp.json()["data"]["id"]

        update_resp = await client.put(
            f"/api/v1/categories/{cat_id}",
            json={"name": "更新后_" + _uuid.uuid4().hex[:6]},
            headers={"Authorization": f"Bearer {setup_data['admin_token']}"},
        )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"].startswith("更新后_")


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_category_empty(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/categories",
            json={"name": "待删除_" + _uuid.uuid4().hex[:6]},
            headers={"Authorization": f"Bearer {setup_data['admin_token']}"},
        )
        cat_id = create_resp.json()["data"]["id"]

        del_resp = await client.delete(
            f"/api/v1/categories/{cat_id}",
            headers={"Authorization": f"Bearer {setup_data['admin_token']}"},
        )
    assert del_resp.status_code == 204


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_category_with_devices(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/v1/categories")
        categories = list_resp.json()["data"]
        cat_with_devices = next((c for c in categories if c["device_count"] > 0), None)
        if cat_with_devices:
            del_resp = await client.delete(
                f"/api/v1/categories/{cat_with_devices['id']}",
                headers={"Authorization": f"Bearer {setup_data['admin_token']}"},
            )
            assert del_resp.status_code == 400