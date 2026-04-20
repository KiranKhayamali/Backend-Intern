from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from ..core.schemas import TimestampSchema, PersistentDeletion, UUIDSchema
from datetime import datetime


class CommentBase(BaseModel):
    content:Annotated[str, Field(min_length=1, max_length=500)]


class Comment(CommentBase, TimestampSchema, PersistentDeletion, UUIDSchema):
    author_id: int 
    post_id: int


class CommentRead(BaseModel):
    id: int 
    content: str 
    author_id: int 
    post_id: int
    author_name:str 
    post_title:str
    # likes: int = 0
    created_at: datetime


class CommentCreate(CommentBase):
    model_config = ConfigDict(extra="forbid")


class CommentCreateInternal(CommentBase):
    author_id: int 
    post_id: int
    author_name:str 
    post_title:str


class CommentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: Annotated[str, Field(min_length=1, max_length=500, default=None)]


class CommentUpdateInternal(CommentUpdate):
    updated_at: datetime


class CommentDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool = True
    deleted_at: datetime

