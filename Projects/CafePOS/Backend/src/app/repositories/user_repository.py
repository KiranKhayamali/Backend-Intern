from typing import List
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from ..core.db.session import SessionDep
from ..models.users import User
from ..schemas.user import UserRead, UserCreate, UserUpdate
from ..core.utils.security import get_password_hash


class UserRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    async def get_all_users(self) -> List[UserRead]:
        result = await self.db.execute(select(User).options(selectinload(User.orders)))
        users = result.scalars().all()
        return users

    async def get_user_by_id(self, user_id: str) -> UserRead:
        result = await self.db.execute(select(User).where(User.id == user_id).options(selectinload(User.orders)))
        user = result.scalars().first()
        if not user:
            raise ValueError("User not Found!")

        return user

    async def get_user_by_contact_number(self, contact_number: str) -> UserRead | None:
        result = await self.db.execute(select(User).where(User.contact_number == contact_number).options(selectinload(User.orders)))
        user = result.scalar_one_or_none()
        if not user:
            return None

        return user

    async def get_user_by_contact_number_excluding_id(self, contact_number: str, user_id: str) -> UserRead | None:
        result = await self.db.execute(
            select(User)
            .where(User.contact_number == contact_number, User.id != user_id)
            .options(selectinload(User.orders))
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        return user

    async def create_user(self, user_create: UserCreate) -> UserRead:
        existing_user = await self.get_user_by_contact_number(user_create.contact_number)
        if existing_user:
            raise ValueError("User with this contact number already exists!")

        user = user_create.model_dump()
        user["hashed_password"] = get_password_hash(user["password"])
        del user["password"]

        new_user = User(**user)
        self.db.add(new_user)
        try:
            await self.db.commit()
            await self.db.refresh(new_user)
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError("User with this contact number already exists!") from e
        return new_user

    async def update_user(self, user_id: str, user_update: UserUpdate) -> UserRead | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise ValueError("User not Found!")

        updated_data = user_update.model_dump(exclude_unset=True)
        contact_number = updated_data.get("contact_number")
        if contact_number:
            existing_user = await self.get_user_by_contact_number_excluding_id(contact_number, user_id)
            if existing_user:
                raise ValueError("User with this contact number already exists!")

        for key, value in updated_data.items():
            setattr(user, key, value)

        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
        except IntegrityError as e:
            await self.db.rollback()
            raise ValueError("User with this contact number already exists!") from e
        return user

    async def delete_user(self, user_id: str) -> dict:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise ValueError("User not Found!")

        await self.db.delete(user)
        await self.db.commit()
        return {"message": f"{user.first_name} {user.last_name} has been deleted successfully!"}
