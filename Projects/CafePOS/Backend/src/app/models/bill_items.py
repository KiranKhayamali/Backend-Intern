from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from uuid6 import uuid7
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .bills import Bill


class BillItem(Base):
    __tablename__ = "bill_items"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), primary_key=True, nullable=False, insert_default=uuid7, init=False)
    bill_id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), ForeignKey("bills.id", ondelete="CASCADE"), nullable=False)
    dish_id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False)
    dish_name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)

    bill: Mapped["Bill"] = relationship("Bill", back_populates="items", init=False)
