from datetime import datetime, UTC
from ..core.db import Base 
from sqlalchemy import JSON, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import EmailStr
from uuid import UUID, uuid7
import uuid as uuid_pkg
from .posts import Post
from .comments import Comment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False) #init = False to prevent it from being passed during object creation

    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[EmailStr] = mapped_column(String(30), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    
    profile_picture: Mapped[str] = mapped_column(default="https://unsplash.com/photos/a-gorilla-sitting-on-the-ground-QGdmkyLK7jo")
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default_factory=uuid7)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    tier_id: Mapped[int | None] = mapped_column(ForeignKey("tiers.id"), index=True, default= None, init=False)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author")
    liked_posts: Mapped[list[str]] = mapped_column(JSON, default=list)
    liked_comments: Mapped[list[str]] = mapped_column(JSON, default=list)