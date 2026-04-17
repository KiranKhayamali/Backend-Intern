from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING
from datetime import datetime, UTC


if TYPE_CHECKING:
    from .users import User
    from .posts import Post


class Comment(Base):

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)

    author: Mapped["User"] = relationship("User", back_populates="comments", init=False)
    comments_of_post: Mapped["Post"] = relationship("Post", back_populates="comments_on_post", init=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    author_name: Mapped[str] = mapped_column(String(20), nullable=False)
    post_title: Mapped[str] = mapped_column(String(50), nullable=False)
    # liked_by_users: Mapped[list["User"]] = relationship("User", secondary="comment_likes", back_populates="liked_comments")
    # likes: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
