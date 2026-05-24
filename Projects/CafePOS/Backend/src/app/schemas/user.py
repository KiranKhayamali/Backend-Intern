from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from enum import Enum

from ..core.schemas import TimestampSchema, UUIDSchema


class RoleEnum(str, Enum):
    chef = "chef"
    receptionist = "receptionist"
    waiter = "waiter"


class UserBase(BaseModel):
    first_name: Annotated[str, Field(min_length=1, max_length=20, examples=["Ram"])]
    middle_name: Annotated[str, Field(max_length=20, examples=["Kumar"])] | None = None
    last_name: Annotated[str, Field(min_length=1, max_length=20, examples=["Shrestha"])]
    contact_number: Annotated[str, Field(min_length=10, max_length=10, examples=["9876543210"])]
    is_admin: bool = Field(default=False)
    role: Annotated[RoleEnum, Field(default=RoleEnum.waiter)] = RoleEnum.waiter


class User(UserBase, UUIDSchema, TimestampSchema):
    hashed_password: str


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    password: Annotated[str, Field(min_length=8, max_length=128, examples=["password123", "MyStrongPassword!"])]


class UserCreateInternal(UserCreate):
    hashed_password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: Annotated[str, Field(min_length=1, max_length=20, examples=["Ram"])] | None = None
    middle_name: Annotated[str | None, Field(max_length=20, examples=["Kumar"])] = None
    last_name: Annotated[str, Field(min_length=1, max_length=20, examples=["Shrestha"])] | None = None
    contact_number: Annotated[str, Field(min_length=10, max_length=10, examples=["9876543210"])] | None = None
    password: Annotated[str, Field(min_length=8, max_length=128, examples=["password123", "MyStrongPassword!"])] | None = None
    is_admin: bool | None = None
    role: RoleEnum | None = None


class UserUpdateInternal(UserUpdate):
    hashed_password: str | None = None
    updated_at: datetime

