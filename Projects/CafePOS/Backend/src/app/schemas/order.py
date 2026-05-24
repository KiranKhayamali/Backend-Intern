from typing import Annotated, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from enum import Enum

from ..core.schemas import TimestampSchema, UUIDSchema
from .item import ItemRead
from .table import TableRead
from .user import UserRead


class OrderStatusEnum(str, Enum):
    idle = "idle"
    pending = "pending"
    in_progress = "in_progress"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"
    open = "open"
    closed = "closed"


class OrderBase(BaseModel):
    items: Annotated[List[ItemRead], Field(default_factory=list)]
    status: OrderStatusEnum | None = None
    remark: Annotated[str, Field(max_length=255, examples=["Customer prefers less spicy food", "Allergic to nuts"])] | None = None


class Order(OrderBase, UUIDSchema, TimestampSchema):
    pass


class OrderRead(OrderBase):
    table: TableRead | None = None
    user: UserRead | None = None
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    table_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])]
    user_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])]
    status: OrderStatusEnum | None = None
    remark: Annotated[str, Field(max_length=255, examples=["Customer prefers less spicy food", "Allergic to nuts"])] | None = None

    model_config = ConfigDict(extra="forbid")


class OrderCreateInternal(OrderCreate):
    pass


class OrderUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])] | None = None
    user_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])] | None = None
    items: Annotated[List[UUID], Field(min_length=1, examples=[[UUID("12345678-1234-1234-1234-123456789012")], [UUID("12345678-1234-1234-1234-123456789012")]])] | None = None
    status: OrderStatusEnum | None = None
    remark: Annotated[str, Field(max_length=255, examples=["Customer prefers less spicy food", "Allergic to nuts"])] | None = None
