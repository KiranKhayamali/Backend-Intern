from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum, String, DateTime, ForeignKey
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid6 import uuid7

from .base import Base

if TYPE_CHECKING:
    from .users import User
    from .tables import Table
    from .items import Item


class OrderStatusEnum(str, Enum):
    idle = "idle"
    pending = "pending"
    in_progress = "in_progress"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"
    open = "open"
    closed = "closed"



class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), primary_key=True, nullable=False, insert_default=uuid7, init=False)
    table_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[OrderStatusEnum] = mapped_column(SQLAlchemyEnum(OrderStatusEnum, name="order_status_enum"), nullable=False, default=OrderStatusEnum.pending)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)

    table: Mapped["Table"] = relationship("Table", back_populates="orders", init=False)
    user: Mapped["User"] = relationship("User", back_populates="orders", init=False)
    items: Mapped[List["Item"]] = relationship("Item", back_populates="order", cascade="all, delete-orphan", init=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default_factory=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None, onupdate=datetime.now)
