from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from datetime import datetime
from typing import TYPE_CHECKING
from uuid6 import uuid7
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum

from .base import Base

if TYPE_CHECKING:
    from .sections import Section
    from .orders import Order
    from .bills import Bill


class TableStatusEnum(str,Enum):
    available = "available"
    occupied = "occupied"
    reserved = "reserved"
    cleaning = "cleaning"


class Table(Base):
    __tablename__ = "tables"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), primary_key=True, nullable=False, insert_default=uuid7, init=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TableStatusEnum] = mapped_column(SQLAlchemyEnum(TableStatusEnum, name="table_status_enum"), nullable=False, default=TableStatusEnum.available)
    section_id: Mapped[UUID | None] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("sections.id", ondelete="SET NULL"), nullable=True, default=None
    )

    section: Mapped["Section | None"] = relationship("Section", back_populates="tables", init=False)
    orders: Mapped["Order"] = relationship("Order", back_populates="table", cascade="all, delete-orphan", init=False)
    bills: Mapped[list["Bill"]] = relationship("Bill", back_populates="table", init=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default_factory=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None, onupdate=datetime.now)
