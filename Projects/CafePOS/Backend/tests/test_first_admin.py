import pytest
from unittest.mock import AsyncMock, patch

from Projects.CafePOS.Backend.src.app.core.utils.first_admin import create_first_admin_user, initialize_first_admin_user


@pytest.mark.asyncio
async def test_create_first_admin_user_creates_when_not_exists():
    mock_repo = AsyncMock()
    mock_repo.get_user_by_contact_number.return_value = None  # Simulate no existing admin

    with patch("src.app.core.utils.first_admin.admin_settings") as mock_settings:
        mock_settings.ADMIN_USER_FIRST_NAME = "Admin"
        mock_settings.ADMIN_USER_LAST_NAME = "User"
        mock_settings.ADMIN_USER_CONTACT_NUMBER = "1111111111"
        mock_settings.ADMIN_USER_IS_ADMIN = True
        mock_settings.ADMIN_USER_ROLE = "receptionist"
        mock_settings.ADMIN_USER_PASSWORD = "admin123"
        await create_first_admin_user(mock_repo)

        mock_repo.get_user_by_contact_number.assert_awaited_once_with("1111111111")
        mock_repo.create_user.assert_awaited_once()

        created_user = mock_repo.create_user.call_args.args[0]
        assert created_user.first_name == "Admin"
        assert created_user.last_name == "User"
        assert created_user.contact_number == "1111111111"
        assert created_user.is_admin is True
        assert created_user.role == "receptionist"


@pytest.mark.asyncio
async def test_create_first_admin_user_does_not_create_if_exists():
    mock_repo = AsyncMock()
    mock_repo.get_user_by_contact_number.return_value = {
        "id": "019e19f9-1144-73f3-9385-4006d815cfa0",
        "contact_number": "1111111111"
    }
    await create_first_admin_user(mock_repo)
    mock_repo.create_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_initialize_first_admin_user_handles_exceptions(capsys):
    mock_repo = AsyncMock()
    mock_repo.get_user_by_contact_number.side_effect = Exception("Database error")
    await initialize_first_admin_user(mock_repo)
    captured = capsys.readouterr()
    assert "Error initializing first admin user: Database error" in captured.out

