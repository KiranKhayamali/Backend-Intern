from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import UTC, datetime
from .base import Base

if TYPE_CHECKING:
    from .users import User
    from .comments import Comment


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    author: Mapped["User"] = relationship("User", back_populates="posts", init=False)
    comments_on_post: Mapped["Comment"] = relationship(
        "Comment", back_populates="comments_of_post", init=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    author_name: Mapped[str] = mapped_column(String(20), nullable=False)
    number_of_comments: Mapped[int] = mapped_column(default=0)
    view_count: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default_factory=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
