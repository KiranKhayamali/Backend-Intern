import pytest
from unittest.mock import AsyncMock, patch


from Projects.CafePOS.Backend.src.app.dependencies.auth_dependency import get_current_user
from Projects.CafePOS.Backend.src.app.core.exceptions.http_exceptions import UnauthorizedException, NotFoundException
from .test_user import _fake_non_admin_user


@pytest.mark.asyncio
async def test_get_current_user_success():
    fake_db = AsyncMock()

    with patch(
        "src.app.dependencies.auth_dependency.decode_token",
        new_callable=AsyncMock
    ) as mock_decode_token, patch(
        "src.app.dependencies.auth_dependency.UserService"
    ) as mock_user_service:
        mock_decode_token.return_value = {"sub": "1234567890"}
        fake_user = await _fake_non_admin_user()
        mock_service_instance = AsyncMock()
        mock_service_instance.get_user_by_contact_number.return_value = fake_user
        mock_user_service.return_value = mock_service_instance

        result = await get_current_user(
            token="fake_token",
            db=fake_db
        )
        mock_decode_token.assert_awaited_once_with("fake_token")
        mock_service_instance.get_user_by_contact_number.assert_awaited_once_with("1234567890")

        assert result.contact_number == fake_user.contact_number


@pytest.mark.asyncio
async def test_get_current_user_invalid_payload():
    fake_db = AsyncMock()

    with patch(
        "src.app.dependencies.auth_dependency.decode_token",
        new_callable=AsyncMock
    ) as mock_decode_token:
        mock_decode_token.return_value = {}
        with pytest.raises(UnauthorizedException) as exc:
            await get_current_user(
                token="bad_token",
                db=fake_db
            )

        assert str(exc.value.detail) == "Invalid token payload!"


@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    fake_db = AsyncMock()

    with patch(
        "src.app.dependencies.auth_dependency.decode_token",
        new_callable=AsyncMock
    ) as mock_decode_token, patch(
        "src.app.dependencies.auth_dependency.UserService"
    ) as mock_user_service:
        mock_decode_token.return_value = {"sub": "1234567890"}
        mock_service_instance = AsyncMock()
        mock_service_instance.get_user_by_contact_number.return_value = None
        mock_user_service.return_value = mock_service_instance

        with pytest.raises(NotFoundException) as exc:
            await get_current_user(
                token="valid_token_but_no_user",
                db=fake_db
            )

        assert str(exc.value.detail) == "User not Found!"


@pytest.mark.asyncio
async def test_get_current_user_returns_existing_object():
    fake_db = AsyncMock()
    fake_user = await _fake_non_admin_user()

    with patch(
        "src.app.dependencies.auth_dependency.decode_token",
        new_callable=AsyncMock
    ) as mock_decode_token, patch(
        "src.app.dependencies.auth_dependency.UserService"
    ) as mock_user_service:
        mock_decode_token.return_value = {"sub": "1234567890"}
        mock_service_instance = AsyncMock()
        mock_service_instance.get_user_by_contact_number.return_value = fake_user
        mock_user_service.return_value = mock_service_instance
        result = await get_current_user(
            token="fake_token",
            db=fake_db
        )

        assert result is fake_user
