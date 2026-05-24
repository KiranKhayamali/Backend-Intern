from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from sqlalchemy import String, DateTime, Integer, ForeignKey, Enum as SQLAlchemyEnum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid6 import uuid7

from .base import Base


if TYPE_CHECKING:
    from .dishes import Dish
    from .orders import Order


class ItemStatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"


class Item(Base):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), primary_key=True, nullable=False, insert_default=uuid7, init=False)
    order_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    dish_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[ItemStatusEnum] = mapped_column(SQLAlchemyEnum(ItemStatusEnum, name="item_status_enum"), nullable=False, default=ItemStatusEnum.pending)

    order: Mapped["Order"] = relationship("Order", back_populates="items", init=False)
    dish: Mapped["Dish"] = relationship("Dish", back_populates="items", init=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default_factory=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None, onupdate=datetime.now)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity"),
    )