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
            id=uid, username=f"it_auth_{uid[:8]}", password_hash=hash_password("Test123456"),
            nickname="测试", role="user", status="active",
        )
        db.add(user)
        await db.commit()

    results["user"] = user
    results["token"] = create_access_token({"sub": str(user.id)})
    yield results


@pytest.mark.asyncio(loop_scope="session")
async def test_register_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/register", json={
            "username": f"reg_{_uuid.uuid4().hex[:8]}",
            "password": "Test123456",
            "nickname": "新用户",
        })
    assert resp.status_code == 201


@pytest.mark.asyncio(loop_scope="session")
async def test_register_duplicate(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/register", json={
            "username": setup_data["user"].username,
            "password": "Test123456",
            "nickname": "重复",
        })
    assert resp.status_code == 409


@pytest.mark.asyncio(loop_scope="session")
async def test_login_success(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/login", json={
            "username": setup_data["user"].username,
            "password": "Test123456",
        })
    assert resp.status_code == 200
    assert "access_token" in resp.json()["data"]


@pytest.mark.asyncio(loop_scope="session")
async def test_login_wrong_password(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/login", json={
            "username": setup_data["user"].username,
            "password": "WrongPass1",
        })
    assert resp.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_get_me(setup_data):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {setup_data['token']}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["username"] == setup_data["user"].username


@pytest.mark.asyncio(loop_scope="session")
async def test_get_me_no_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio(loop_scope="session")
async def test_refresh_token(setup_data):
    from app.core.security import create_refresh_token
    rt = create_refresh_token({"sub": str(setup_data["user"].id)})
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {rt}"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()["data"]


@pytest.mark.asyncio(loop_scope="session")
async def test_register_invalid_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/auth/register", json={
            "username": f"badpw_{_uuid.uuid4().hex[:8]}",
            "password": "short",
            "nickname": "坏密码",
        })
    assert resp.status_code == 422