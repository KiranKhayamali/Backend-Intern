from typing import List
from fastapi import HTTPException, status

from ..core.deps import SessionDep
from ..schemas.user import UserRead, UserCreate, UserUpdate
from ..repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: SessionDep):
        self.repo = UserRepository(db)

    async def get_all_users(self) -> List[UserRead]:
        return await self.repo.get_all_users()

    async def create_user(self, user_data: UserCreate) -> UserRead:
        try:
            return await self.repo.create_user(user_data)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserRead:
        try:
            return await self.repo.update_user(user_id, user_data)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_user_by_username(self, username: str) -> UserRead:
        try:
            return await self.repo.get_user_by_username(username)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))