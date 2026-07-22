import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.database import async_session_factory
from app.core.security import hash_password, create_access_token
from app.models.user import User

import uuid as _uuid


@pytest_asyncio.fixture
async def setup_data():
    results = {}

    async with async_session_factory() as db:
        uid = str(_uuid.uuid4())
        user = User(
            id=uid, username=f"prof_user_{uid[:8]}", password_hash=hash_password("Test123456"),
            nickname="测试用户", role="user", status="active",
        )
        db.add(user)
        await db.commit()

    results["user"] = user
    results["token"] = create_access_token({"sub": str(user.id)})
    yield results


@pytest.mark.asyncio(loop_scope="session")
async def test_update_profile(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.put(
            "/api/v1/users/me",
            json={"nickname": "新昵称", "phone": "13800138000"},
            headers={"Authorization": f"Bearer {setup_data['token']}"},
        )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["nickname"] == "新昵称"


@pytest.mark.asyncio(loop_scope="session")
async def test_change_password(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.put(
            "/api/v1/users/me/password",
            json={"old_password": "Test123456", "new_password": "Newpass123"},
            headers={"Authorization": f"Bearer {setup_data['token']}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_change_password_wrong_old(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.put(
            "/api/v1/users/me/password",
            json={"old_password": "WrongPass1", "new_password": "Newpass123"},
            headers={"Authorization": f"Bearer {setup_data['token']}"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_get_my_devices(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/users/me/devices",
            headers={"Authorization": f"Bearer {setup_data['token']}"},
        )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "items" in data
    assert "total" in data