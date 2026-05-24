from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from enum import Enum

from ..core.schemas import TimestampSchema, UUIDSchema
from .table import TableRead
from .user import UserRead


class paymentMethodEnum(str, Enum):
    cash = "cash"
    card = "card"
    mobile_payment = "mobile payment"


class BillItem(BaseModel):
    dish_name: Annotated[str, Field(max_length=100, examples=["Steamed Buff Momo", "Dry Noodles (Chicken)"])]
    quantity: Annotated[int, Field(gt=0, examples=[1, 2, 3])]
    unit_price: Annotated[int, Field(gt=0, examples=[150, 200, 250])]
    total_price: Annotated[int, Field(gt=0, examples=[150, 400, 750])]

    model_config = ConfigDict(from_attributes=True)


class BillBase(BaseModel):
    customer_name: Annotated[str, Field(max_length=100, examples=["Rajesh Hamal", "Sujan Chapagain"])] | None = None
    customer_contact: Annotated[str, Field(max_length=20, examples=["+9876543210", "+9876012345"])] | None = None

    payment_method: paymentMethodEnum = paymentMethodEnum.cash


class Bill(BillBase, UUIDSchema, TimestampSchema):
    billed_at: Annotated[datetime, Field(description="Date and time when the bill was generated", examples=["2024-01-01T12:00:00Z"])]


class BillRead(BillBase):
    id: UUID
    table: TableRead | None = None
    items: Annotated[list[BillItem], Field(description="List of individual items with their quantities and prices")]
    total_amount: Annotated[int, Field(gt=0, examples=[350, 500])]
    user: UserRead | None = None
    billed_at: Annotated[datetime, Field(description="Date and time when the bill was generated", examples=["2024-01-01T12:00:00Z"])] | None = None

    model_config = ConfigDict(from_attributes=True)


class BillCreate(BillBase):
    order_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])]
    table_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])]
    user_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])]
    model_config = ConfigDict(extra="forbid")


class BillCreateInternal(BillCreate):
    billed_at: datetime


class BillUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])] | None = None
    table_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])] | None = None
    user_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])] | None = None
    customer_name: Annotated[str, Field(max_length=100, examples=["Rajesh Hamal", "Sujan Chapagain"])] | None = None
    customer_contact: Annotated[str, Field(max_length=20, examples=["+9876543210", "+9876012345"])] | None = None

    payment_method: paymentMethodEnum | None = None


class BillUpdateInternal(BillUpdate):
    updated_at: datetime
