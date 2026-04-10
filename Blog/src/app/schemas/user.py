from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Annotated
from datetime import datetime

from ..core.schemas import UUIDSchema, TimestampSchema, PersistentDeletion


class UserBase(BaseModel):
    username: Annotated[str, Field(min_length=2, max_length=20)]
    email: Annotated[EmailStr, Field(min_length=5, max_length=30, examples=["user@example.com", "user.name@example.com"])] 


class User(UUIDSchema, UserBase, TimestampSchema, PersistentDeletion):
    profile_picture: Annotated[str, Field(default="https://unsplash.com/photos/a-gorilla-sitting-on-the-ground-QGdmkyLK7jo")]
    hashed_password: str 
    is_admin: bool = False
    posts: list | None = None  # This will be populated with the user's posts when needed


class UserRead(BaseModel):
    id: int | None = None 
    username: Annotated[str, Field(min_length=3, max_length=100)]
    email: Annotated[EmailStr, Field(examples=["user@example.com", "user.name@example.com"])] 
    profile_picture: Annotated[str, Field(examples=["https://unsplash.com/photos/a-gorilla-sitting-on-the-ground-QGdmkyLK7jo"], default=None)]

class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid") # raise error if extra fields are provided

    password: Annotated[str, Field(min_length=6, max_length=20, examples=["Password1", "MySecurePass123"])] 

class UserCreateInternal(UserBase):
    hashed_password: str

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Annotated[str, Field(min_length=3, max_length=100, default=None)] 
    email: Annotated[EmailStr, Field(examples=["user@example.com", "user.name@example.com"], default=None)] 
    profile_picture: Annotated[str, Field(examples=["https://unsplash.com/photos/a-gorilla-sitting-on-the-ground-QGdmkyLK7jo"], default=None)]
    
class UserUpdateInternal(UserUpdate):
    updated_at: datetime


class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool = True
    deleted_at: datetime 

class UserRestoreDelete(BaseModel):
    is_deleted: bool = False
