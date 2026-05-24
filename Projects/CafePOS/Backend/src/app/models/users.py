from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List
from uuid import UUID
from enum import Enum
from sqlalchemy import String, Boolean, DateTime, Enum as SQLAlchemyEnum
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from uuid6 import uuid7


from .base import Base

if TYPE_CHECKING:
    from .orders import Order
    from .bills import Bill


class RoleEnum(str, Enum):
    chef = "chef"
    receptionist = "receptionist"
    waiter = "waiter"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), primary_key=True, nullable=False, insert_default=uuid7, init=False)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_number: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user", init=False)
    bills: Mapped[List["Bill"]] = relationship("Bill", back_populates="user", init=False)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(SQLAlchemyEnum(RoleEnum, name="role_enum"), default=RoleEnum.waiter, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default_factory=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None, onupdate=datetime.now)