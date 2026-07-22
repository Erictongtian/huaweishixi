import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from decimal import Decimal

from app.services.device_service import (
    create_device, get_devices, get_device_detail, update_device,
    update_price, toggle_status, delete_device, add_device_image, delete_device_image,
)
from app.schemas.device import DeviceCreate, DeviceUpdate, PriceUpdate, StatusUpdate
from app.core.exceptions import BusinessException, ConflictException, NotFoundException, PermissionException


def _mock_db():
    return AsyncMock()


def _mock_device(**overrides):
    d = MagicMock()
    d.id = uuid4()
    d.title = "测试设备"
    d.seller_id = uuid4()
    d.category_id = uuid4()
    d.price = Decimal("100.00")
    d.original_price = None
    d.condition_level = "almost_new"
    d.usage_duration = None
    d.description = None
    d.location = None
    d.contact_info = None
    d.status = "on_sale"
    d.view_count = 0
    d.images = []
    d.created_at = "2026-01-01"
    d.updated_at = "2026-01-01"
    for k, v in overrides.items():
        setattr(d, k, v)
    return d


class TestDeviceCreate:
    @pytest.mark.asyncio
    async def test_create_success(self):
        db = _mock_db()
        uid = uuid4()
        req = DeviceCreate(
            title="设备", category_id=uuid4(), price=Decimal("99"),
            condition_level="almost_new",
        )
        cat_mock = MagicMock()
        cat_mock.id = req.category_id
        cat_mock.name = "分类"
        call_count = [0]
        def mock_execute(stmt):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(scalar_one_or_none=MagicMock(return_value=cat_mock))
            return MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
        db.execute = AsyncMock(side_effect=mock_execute)
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        with patch("app.services.device_service.DeviceCreateResponse.model_validate", return_value=MagicMock()):
            with patch("app.services.device_service.selectinload"):
                result = await create_device(db, uid, req)
        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_category_not_found(self):
        db = _mock_db()
        req = DeviceCreate(
            title="设备", category_id=uuid4(), price=Decimal("99"),
            condition_level="almost_new",
        )
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(NotFoundException):
            await create_device(db, uuid4(), req)


class TestDeviceGetDetail:
    @pytest.mark.asyncio
    async def test_get_detail_not_found(self):
        db = _mock_db()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(NotFoundException):
            await get_device_detail(db, uuid4())


class TestDeviceUpdate:
    @pytest.mark.asyncio
    async def test_update_not_owner(self):
        db = _mock_db()
        uid = uuid4()
        mock_dev = _mock_device(seller_id=uuid4())
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_dev)))
        with pytest.raises(PermissionException):
            await update_device(db, uuid4(), uid, DeviceUpdate(title="新"))

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        db = _mock_db()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(NotFoundException):
            await update_device(db, uuid4(), uuid4(), DeviceUpdate(title="新"))


class TestDevicePrice:
    @pytest.mark.asyncio
    async def test_update_price_not_owner(self):
        db = _mock_db()
        mock_dev = _mock_device(seller_id=uuid4())
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_dev)))
        with pytest.raises(PermissionException):
            await update_price(db, uuid4(), uuid4(), PriceUpdate(price=50))

    @pytest.mark.asyncio
    async def test_update_price_sold_device(self):
        db = _mock_db()
        uid = uuid4()
        mock_dev = _mock_device(seller_id=uid, status="sold")
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_dev)))
        with pytest.raises(BusinessException):
            await update_price(db, uuid4(), uid, PriceUpdate(price=50))


class TestDeviceStatus:
    @pytest.mark.asyncio
    async def test_toggle_not_owner(self):
        db = _mock_db()
        mock_dev = _mock_device(seller_id=uuid4())
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_dev)))
        with pytest.raises(PermissionException):
            await toggle_status(db, uuid4(), uuid4(), StatusUpdate(action="off_shelf"))

    @pytest.mark.asyncio
    async def test_toggle_off_shelf_with_active_order(self):
        db = _mock_db()
        uid = uuid4()
        mock_dev = _mock_device(seller_id=uid, status="on_sale")
        call_count = [0]
        def mock_execute(stmt):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(scalar_one_or_none=MagicMock(return_value=mock_dev))
            return MagicMock(scalar=MagicMock(return_value=1))
        db.execute = AsyncMock(side_effect=mock_execute)
        with pytest.raises(ConflictException):
            await toggle_status(db, uuid4(), uid, StatusUpdate(action="off_shelf"))

    @pytest.mark.asyncio
    async def test_toggle_sold_device(self):
        db = _mock_db()
        uid = uuid4()
        mock_dev = _mock_device(seller_id=uid, status="sold")
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_dev)))
        with pytest.raises(BusinessException):
            await toggle_status(db, uuid4(), uid, StatusUpdate(action="off_shelf"))


class TestDeviceDelete:
    @pytest.mark.asyncio
    async def test_delete_not_owner(self):
        db = _mock_db()
        mock_dev = _mock_device(seller_id=uuid4())
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_dev)))
        with pytest.raises(PermissionException):
            await delete_device(db, uuid4(), uuid4())

    @pytest.mark.asyncio
    async def test_delete_on_sale_device(self):
        db = _mock_db()
        uid = uuid4()
        mock_dev = _mock_device(seller_id=uid, status="on_sale")
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_dev)))
        with pytest.raises(BusinessException):
            await delete_device(db, uuid4(), uid)