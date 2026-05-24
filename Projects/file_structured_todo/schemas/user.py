from pydantic import BaseModel
from typing import List
from datetime import datetime

from .note import NoteRead

class UserBase(BaseModel):
    username: str
    is_admin: bool = False


class UserSchema(UserBase):
    password: str


class UserRead(UserBase):
    id: int | None = None
    username: str
    notes: List[NoteRead] = []

    model_config = {
        "from_attributes": True
    }

class UserCreate(UserSchema):
    model_config = {
        "extra": "forbid"
    }


class UserCreateInternal(UserCreate):
    created_at: datetime | None = None


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    is_admin: bool | None = None

    model_config = {
        "extra": "forbid"
    }


class UserUpdateInternal(UserUpdate):
    updated_at: datetime | None = None