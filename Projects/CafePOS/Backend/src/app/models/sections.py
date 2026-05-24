from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime
from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from uuid6 import uuid7

from .base import Base

if TYPE_CHECKING:
    from .tables import Table


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID(as_uuid=True), primary_key=True, nullable=False, insert_default=uuid7, init=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    tables: Mapped[List["Table"]] = relationship("Table", back_populates="section", cascade="all, delete-orphan", init=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default_factory=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None, onupdate=datetime.now)
