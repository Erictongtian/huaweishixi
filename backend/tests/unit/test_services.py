import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.auth_service import register, authenticate
from app.services.device_service import create_device, get_devices, get_device_detail
from app.services.order_service import create_order, confirm_order, reject_order, complete_order, cancel_order
from app.services.review_service import create_review, get_device_reviews, get_review_stats
from app.services.category_service import get_categories, create_category, update_category, delete_category
from app.services.user_service import update_profile, change_password, get_my_devices
from app.core.exceptions import BusinessException, ConflictException, NotFoundException, PermissionException
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.device import DeviceCreate
from app.schemas.order import OrderCreate, OrderConfirm, OrderCancel
from app.schemas.review import ReviewCreate
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.user import ProfileUpdate, ChangePassword


def _mock_db():
    return AsyncMock()


# ===================== AUTH SERVICE =====================

class TestRegister:
    @pytest.mark.asyncio
    async def test_register_success(self):
        db = _mock_db()
        req = RegisterRequest(username="newuser", password="Test123456", nickname="New")
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        db.flush = AsyncMock()
        with patch("app.services.auth_service.UserResponse.model_validate", return_value=MagicMock()):
            result = await register(db, req)
        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self):
        db = _mock_db()
        req = RegisterRequest(username="dup", password="Test123456", nickname="Dup")
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock())))
        with pytest.raises(ConflictException):
            await register(db, req)

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        db = _mock_db()
        req = RegisterRequest(username="new2", password="Test123456", nickname="N2", email="a@b.com")
        call_count = [0]
        def mock_execute(stmt):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(scalar_one_or_none=MagicMock(return_value=None))
            return MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock()))
        db.execute = AsyncMock(side_effect=mock_execute)
        with pytest.raises(ConflictException):
            await register(db, req)


class TestAuthenticate:
    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        db = _mock_db()
        req = LoginRequest(username="user", password="wrong1")
        mock_user = MagicMock()
        mock_user.status = "active"
        mock_user.fail_count = 0
        mock_user.locked_until = None
        mock_user.password_hash = "hash"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))
        with patch("app.services.auth_service.verify_password", return_value=False):
            with pytest.raises(BusinessException):
                await authenticate(db, req)

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        db = _mock_db()
        req = LoginRequest(username="nobody", password="Test123456")
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(BusinessException):
            await authenticate(db, req)


# ===================== ORDER SERVICE =====================

class TestOrderService:
    @pytest.mark.asyncio
    async def test_create_order_device_not_found(self):
        db = _mock_db()
        req = OrderCreate(device_id=uuid4())
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(NotFoundException):
            await create_order(db, uuid4(), req)

    @pytest.mark.asyncio
    async def test_create_order_own_device(self):
        db = _mock_db()
        uid = uuid4()
        req = OrderCreate(device_id=uuid4())
        mock_device = MagicMock()
        mock_device.seller_id = uid
        mock_device.status = "on_sale"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_device)))
        with pytest.raises(PermissionException):
            await create_order(db, uid, req)

    @pytest.mark.asyncio
    async def test_create_order_not_on_sale(self):
        db = _mock_db()
        uid = uuid4()
        req = OrderCreate(device_id=uuid4())
        mock_device = MagicMock()
        mock_device.seller_id = uuid4()
        mock_device.status = "off_shelf"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_device)))
        with pytest.raises(BusinessException):
            await create_order(db, uid, req)

    @pytest.mark.asyncio
    async def test_confirm_order_not_seller(self):
        db = _mock_db()
        mock_order = MagicMock()
        mock_order.seller_id = uuid4()
        mock_order.status = "pending"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_order)))
        with pytest.raises(PermissionException):
            await confirm_order(db, uuid4(), uuid4(), OrderConfirm())

    @pytest.mark.asyncio
    async def test_reject_order_not_pending(self):
        db = _mock_db()
        uid = uuid4()
        mock_order = MagicMock()
        mock_order.seller_id = uid
        mock_order.status = "confirmed"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_order)))
        with pytest.raises(BusinessException):
            await reject_order(db, uuid4(), uid)

    @pytest.mark.asyncio
    async def test_complete_order_not_buyer(self):
        db = _mock_db()
        mock_order = MagicMock()
        mock_order.buyer_id = uuid4()
        mock_order.status = "confirmed"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_order)))
        with pytest.raises(PermissionException):
            await complete_order(db, uuid4(), uuid4())

    @pytest.mark.asyncio
    async def test_cancel_order_not_pending_or_confirmed(self):
        db = _mock_db()
        uid = uuid4()
        mock_order = MagicMock()
        mock_order.buyer_id = uid
        mock_order.seller_id = uid
        mock_order.status = "completed"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_order)))
        with pytest.raises(BusinessException):
            await cancel_order(db, uuid4(), uid, OrderCancel(cancel_reason="test"))


# ===================== REVIEW SERVICE =====================

class TestReviewService:
    @pytest.mark.asyncio
    async def test_create_review_order_not_found(self):
        db = _mock_db()
        req = ReviewCreate(order_id=uuid4(), rating=5)
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(NotFoundException):
            await create_review(db, uuid4(), req)

    @pytest.mark.asyncio
    async def test_create_review_not_buyer(self):
        db = _mock_db()
        req = ReviewCreate(order_id=uuid4(), rating=5)
        mock_order = MagicMock()
        mock_order.buyer_id = uuid4()
        mock_order.status = "completed"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_order)))
        with pytest.raises(PermissionException):
            await create_review(db, uuid4(), req)

    @pytest.mark.asyncio
    async def test_create_review_order_not_completed(self):
        db = _mock_db()
        uid = uuid4()
        req = ReviewCreate(order_id=uuid4(), rating=5)
        mock_order = MagicMock()
        mock_order.buyer_id = uid
        mock_order.status = "confirmed"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_order)))
        with pytest.raises(BusinessException):
            await create_review(db, uid, req)

    @pytest.mark.asyncio
    async def test_create_review_duplicate(self):
        db = _mock_db()
        uid = uuid4()
        req = ReviewCreate(order_id=uuid4(), rating=5)
        mock_order = MagicMock()
        mock_order.buyer_id = uid
        mock_order.status = "completed"
        call_count = [0]
        def mock_execute(stmt):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(scalar_one_or_none=MagicMock(return_value=mock_order))
            return MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock()))
        db.execute = AsyncMock(side_effect=mock_execute)
        with pytest.raises(ConflictException):
            await create_review(db, uid, req)


# ===================== CATEGORY SERVICE =====================

class TestCategoryService:
    @pytest.mark.asyncio
    async def test_create_category_duplicate_name(self):
        db = _mock_db()
        req = CategoryCreate(name="dup")
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock())))
        with pytest.raises(ConflictException):
            await create_category(db, req)

    @pytest.mark.asyncio
    async def test_update_category_not_found(self):
        db = _mock_db()
        req = CategoryUpdate(name="x")
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(NotFoundException):
            await update_category(db, uuid4(), req)

    @pytest.mark.asyncio
    async def test_delete_category_with_devices(self):
        db = _mock_db()
        cat_id = uuid4()
        mock_cat = MagicMock()
        call_count = [0]
        def mock_execute(stmt):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(scalar_one_or_none=MagicMock(return_value=mock_cat))
            return MagicMock(scalar=MagicMock(return_value=5))
        db.execute = AsyncMock(side_effect=mock_execute)
        with pytest.raises(BusinessException):
            await delete_category(db, cat_id)

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self):
        db = _mock_db()
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(NotFoundException):
            await delete_category(db, uuid4())


# ===================== USER SERVICE =====================

class TestUserService:
    @pytest.mark.asyncio
    async def test_update_profile_not_found(self):
        db = _mock_db()
        req = ProfileUpdate(nickname="x")
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with pytest.raises(NotFoundException):
            await update_profile(db, uuid4(), req)

    @pytest.mark.asyncio
    async def test_change_password_wrong_old(self):
        db = _mock_db()
        uid = uuid4()
        req = ChangePassword(old_password="wrong1", new_password="Newpass123")
        mock_user = MagicMock()
        mock_user.password_hash = "hash"
        db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user)))
        with patch("app.services.user_service.verify_password", return_value=False):
            with pytest.raises(PermissionException):
                await change_password(db, uid, req)

    @pytest.mark.asyncio
    async def test_update_profile_duplicate_email(self):
        db = _mock_db()
        uid = uuid4()
        req = ProfileUpdate(email="taken@b.com")
        mock_user = MagicMock()
        mock_user.email = "old@b.com"
        call_count = [0]
        def mock_execute(stmt):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(scalar_one_or_none=MagicMock(return_value=mock_user))
            return MagicMock(scalar_one_or_none=MagicMock(return_value=MagicMock()))
        db.execute = AsyncMock(side_effect=mock_execute)
        with pytest.raises(ConflictException):
            await update_profile(db, uid, req)


# ===================== SCHEMA VALIDATION =====================

class TestSchemaValidation:
    def test_review_rating_too_low(self):
        with pytest.raises(ValueError):
            ReviewCreate(order_id=uuid4(), rating=0)

    def test_review_rating_too_high(self):
        with pytest.raises(ValueError):
            ReviewCreate(order_id=uuid4(), rating=6)

    def test_review_rating_valid(self):
        r = ReviewCreate(order_id=uuid4(), rating=3)
        assert r.rating == 3

    def test_register_invalid_username(self):
        with pytest.raises(ValueError):
            RegisterRequest(username="ab", password="Test123456", nickname="N")

    def test_register_invalid_password_no_digit(self):
        with pytest.raises(ValueError):
            RegisterRequest(username="user1", password="abcdefgh", nickname="N")

    def test_register_invalid_password_no_letter(self):
        with pytest.raises(ValueError):
            RegisterRequest(username="user1", password="12345678", nickname="N")

    def test_register_empty_nickname(self):
        with pytest.raises(ValueError):
            RegisterRequest(username="user1", password="Test123456", nickname="  ")

    def test_change_password_valid(self):
        r = ChangePassword(old_password="Old123456", new_password="New123456")
        assert r.new_password == "New123456"

    def test_change_password_invalid_new(self):
        with pytest.raises(ValueError):
            ChangePassword(old_password="Old123456", new_password="short1")

    def test_category_create_defaults(self):
        r = CategoryCreate(name="Test")
        assert r.sort_order == 0
        assert r.icon is None

    def test_profile_update_partial(self):
        r = ProfileUpdate(nickname="New")
        assert r.nickname == "New"
        assert r.phone is None
        assert r.email is None


# ===================== SECURITY =====================

class TestSecurity:
    def test_hash_and_verify_password(self):
        from app.core.security import hash_password, verify_password
        hashed = hash_password("Test123456")
        assert verify_password("Test123456", hashed)
        assert not verify_password("Wrong1", hashed)

    def test_create_and_decode_token(self):
        from app.core.security import create_access_token, decode_token
        token = create_access_token(data={"sub": "user123", "role": "user"})
        payload = decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["role"] == "user"
        assert payload["type"] == "access"

    def test_decode_invalid_token(self):
        from app.core.security import decode_token
        with pytest.raises(ValueError):
            decode_token("invalid.token.here")

    def test_create_refresh_token(self):
        from app.core.security import create_refresh_token, decode_token
        token = create_refresh_token(data={"sub": "user123"})
        payload = decode_token(token)
        assert payload["type"] == "refresh"