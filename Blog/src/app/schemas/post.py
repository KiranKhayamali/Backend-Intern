from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, List, Optional
from datetime import datetime
from ..core.schemas import TimestampSchema, PersistentDeletion, UUIDSchema
from .comment import CommentRead


class PostBase(BaseModel):
    title: Annotated[str, Field(min_length=2, max_length=100)]
    content: Annotated[str, Field(min_length=10, max_length=1000)]
    
    
class Post(PostBase, TimestampSchema, PersistentDeletion, UUIDSchema): 
    author_id: int 

    comments: Optional[List[CommentRead]] = None


class PostRead(BaseModel):
    id: int 
    title: str 
    content: str 
    author_id: int 
    author_name: str
    number_of_comments: int
    view_count: int
    created_at: datetime 


class PostReadWithComments(PostRead):
    comments: List[CommentRead] = []


class PostCreate(PostBase):
    model_config = ConfigDict(extra="forbid")


class PostCreateInternal(PostBase):
    author_id: int
    author_name: str
    

class PostUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str, Field(min_length=2, max_length=200, default=None)]
    content: Annotated[str, Field(min_length=10, max_length=1000, default=None)] 
    

class PostUpdateInternal(PostUpdate):
    updated_at: datetime


class PostDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool = True
    deleted_at: datetime



