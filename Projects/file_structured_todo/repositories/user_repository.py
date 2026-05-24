from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..core.deps import SessionDep
from ..schemas.user import UserRead, UserCreate, UserUpdate
from ..models.users import User
from ..core.utils.auth import get_password_hash


class UserRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    async def get_all_users(self) -> List[UserRead]:
        result = await self.db.execute(select(User).options(selectinload(User.notes)))
        users = result.scalars().all()
        return users

    async def get_user_by_id(self, user_id: int) -> UserRead | None:
        result = await self.db.execute(select(User).where(User.id == user_id).options(selectinload(User.notes)))
        user = result.scalar_one_or_none()
        return user

    async def get_user_by_username(self, username: str) -> UserRead | None:
        result = await self.db.execute(select(User).where(User.username == username).options(selectinload(User.notes)))
        user = result.scalar_one_or_none()
        return user

    async def create_user(self, user_data: UserCreate) -> UserRead:
        existing = await self.get_user_by_username(user_data.username)
        if existing:
            raise ValueError(f"User with username {user_data.username} already exists")

        user = user_data.model_dump()
        user["password"] = get_password_hash(user_data.password)
        db_user = User(**user)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user, ["notes"])
        return db_user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> UserRead:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        if user_data.username and user_data.username != user.username:
            existing = await self.get_user_by_username(user_data.username)
            if existing:
                raise ValueError(f"User with username {user_data.username} already exists")

        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])

        for key, value in update_data.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user, ["notes"])
        return user