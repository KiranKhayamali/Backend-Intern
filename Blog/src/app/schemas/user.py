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
    tier_id: int | None = None
    posts: list | None = None  # This will be populated with the user's posts when needed
    likes: list | None = None  # This will be populated with the user's liked posts when needed
    comments: list | None = None  # This will be populated with the user's comments when needed

class UserRead(BaseModel):
    id: int | None = None 
    username: Annotated[str, Field(min_length=3, max_length=100)]
    email: Annotated[EmailStr, Field(examples=["user@example.com", "user.name@example.com"])] 
    profile_picture: str
    tier_id: int | None = None

class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid") # raise error if extra fields are provided

    password: Annotated[str, Field(min_length=6, max_length=20, pattern=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$", examples=["Password1", "MySecurePass123"])] 

class UserCreateInternal(UserBase):
    hashed_password: str

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: Annotated[str, Field(min_length=3, max_length=100, default=None)] 
    email: Annotated[EmailStr, Field(examples=["user@example.com", "user.name@example.com"], default=None)] 
    profile_picture: Annotated[str, Field(examples=["https://unsplash.com/photos/a-gorilla-sitting-on-the-ground-QGdmkyLK7jo"], default=None)]
    
class UserUpdateInternal(UserUpdate):
    updated_at: datetime

class UserUpdateTier(BaseModel):
    tier_id: int 

class UserDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool = True
    deleted_at: datetime 

class UserRestoreDelete(BaseModel):
    is_deleted: bool = False
