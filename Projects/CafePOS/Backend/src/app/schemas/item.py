from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from enum import Enum

from ..core.schemas import TimestampSchema, UUIDSchema
from .dish import DishRead


class ItemStatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"


class ItemBase(BaseModel):
    quantity: Annotated[int, Field(gt=0, examples=[1, 2, 3])]
    quantity_type: Annotated[str, Field(max_length=20, examples=["plate", "bowl", "piece"])] | None = None
    remark: Annotated[str, Field(max_length=255, examples=["Less spicy", "No onions", "Extra cheese"])] | None = None
    status: Annotated[ItemStatusEnum, Field(max_length=20, examples=["pending", "in_progress", "ready", "delivered", "cancelled"], default=ItemStatusEnum.pending)]


class Item(ItemBase, UUIDSchema, TimestampSchema):
    pass


class ItemRead(ItemBase):
    dish: DishRead | None = None
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class ItemCreate(ItemBase):
    order_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])]
    dish_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])]
    model_config = ConfigDict(extra="forbid")


class ItemCreateInternal(ItemCreate):
    pass


class ItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])] | None = None
    dish_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])] | None = None
    quantity: Annotated[int, Field(gt=0, examples=[1, 2, 3])] | None = None
    quantity_type: Annotated[str, Field(max_length=20, examples=["plate", "bowl", "piece"])] | None = None
    remark: Annotated[str, Field(max_length=255, examples=["Less spicy", "No onions", "Extra cheese"])] | None = None
    status: ItemStatusEnum | None = None


class ItemUpdateInternal(ItemUpdate):
    updated_at: datetime
