from .security import get_password_hash
from ..config import settings
from ...repositories.user_repository import UserRepository
from ...schemas.user import UserCreate

admin_settings = settings


async def create_first_admin_user(repo: UserRepository):
    existing_admin = await repo.get_user_by_contact_number(admin_settings.ADMIN_USER_CONTACT_NUMBER)
    if existing_admin:
        return # Admin user already exists, no need to create

    admin_user_data = {
        "first_name": admin_settings.ADMIN_USER_FIRST_NAME,
        "last_name": admin_settings.ADMIN_USER_LAST_NAME,
        "contact_number": admin_settings.ADMIN_USER_CONTACT_NUMBER,
        "is_admin": admin_settings.ADMIN_USER_IS_ADMIN,
        "role": admin_settings.ADMIN_USER_ROLE,
        # pass raw password; repository/service will hash it
        "password": admin_settings.ADMIN_USER_PASSWORD,
    }

    # validate/construct a UserCreate model before calling repository
    user_create = UserCreate.model_validate(admin_user_data)
    await repo.create_user(user_create)


async def initialize_first_admin_user(repo: UserRepository):
    try:
        await create_first_admin_user(repo)
        print("First admin user initialized successfully!")
    except Exception as e:
        print(f"Error initializing first admin user: {e}")
