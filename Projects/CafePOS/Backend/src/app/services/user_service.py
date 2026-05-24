from typing import List
from uuid import UUID

from ..schemas.user import UserRead, UserCreate, UserUpdate
from ..repositories.user_repository import UserRepository
from ..core.exceptions.http_exceptions import NotFoundException, BadRequestException


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_all_users(self) -> List[UserRead]:
        return [UserRead.model_validate(user) for user in await self.repo.get_all_users()]

    async def get_user_by_id(self, user_id: UUID) -> UserRead:
        try:
            return UserRead.model_validate(await self.repo.get_user_by_id(user_id))
        except ValueError as e:
            raise NotFoundException("User not Found!")

    async def get_user_by_contact_number(self, contact_number: str) -> UserRead:
        try:
            user = await self.repo.get_user_by_contact_number(contact_number)
            if not user:
                raise NotFoundException(f"User with contact number {contact_number} not Found!")
            return UserRead.model_validate(user)
        except Exception as e:
            raise NotFoundException("User not Found!")

    async def create_user(self, user_create: UserCreate) -> UserRead:
        try:
            return UserRead.model_validate(await self.repo.create_user(user_create))
        except ValueError as e:
            raise BadRequestException(str(e))

    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> UserRead:
        try:
            updated_user = await self.repo.update_user(user_id=user_id, user_update=user_update)
            if not updated_user:
                raise NotFoundException("User not Found!")

            return UserRead.model_validate(updated_user)
        except ValueError as e:
            if "already exists" in str(e):
                raise BadRequestException(str(e))
            raise NotFoundException("User not Found!")

        except Exception as e:
            raise BadRequestException(str(e))

    async def delete_user(self, user_id: UUID) -> dict:
        try:
            deleted_user = await self.repo.delete_user(user_id=user_id)
            if not deleted_user:
                raise NotFoundException("User not Found!")

            return deleted_user
        except ValueError:
            raise NotFoundException("User not Found!")

        except Exception as e:
            raise BadRequestException(str(e))

