from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, ForeignKey
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from datetime import datetime
from typing import TYPE_CHECKING
from uuid6 import uuid7
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum

from .base import Base


if TYPE_CHECKING:
    from .bill_items import BillItem
    from .users import User
    from .tables import Table


class paymentMethodEnum(str, Enum):
    cash = "cash"
    card = "card"
    mobile_payment = "mobile payment"


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), primary_key=True, nullable=False, insert_default=uuid7, init=False)
    order_id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    table_id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)
    customer_contact: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)
    payment_method: Mapped[paymentMethodEnum | None] = mapped_column(SQLAlchemyEnum(paymentMethodEnum, name="payment_method_enum"), nullable=True, default=paymentMethodEnum.cash)
    billed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default_factory=datetime.now)

    items: Mapped[list["BillItem"]] = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan", init=False)
    table: Mapped["Table"] = relationship("Table", back_populates="bills", init=False)
    user: Mapped["User"] = relationship("User", back_populates="bills", init=False)


