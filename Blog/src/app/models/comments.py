from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.db.database import Base
from datetime import UTC, datetime
from .users import User


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    likes: Mapped[int] = mapped_column(default=0)
    liked_by_users: Mapped[list["User"]] = relationship("User", secondary="comment_likes", back_populates="liked_comments")