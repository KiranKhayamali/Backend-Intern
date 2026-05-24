from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from datetime import datetime
from typing import TYPE_CHECKING
from uuid6 import uuid7

from .base import Base

if TYPE_CHECKING:
    from .items import Item


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), primary_key=True, nullable=False, insert_default=uuid7, init=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    dish_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    items: Mapped[list["Item"]] = relationship("Item", back_populates="dish", cascade="all, delete-orphan", init=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default_factory=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None, onupdate=datetime.now)
