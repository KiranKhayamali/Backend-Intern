from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from enum import Enum

from ..core.schemas import TimestampSchema, UUIDSchema
from .section import SectionRead


class TableStatusEnum(str,Enum):
    available = "available"
    occupied = "occupied"
    reserved = "reserved"
    cleaning = "cleaning"


class TableBase(BaseModel):
    number: Annotated[int, Field(gt=0, examples=[1, 2, 3])]
    capacity: Annotated[int, Field(gt=0, examples=[2, 4, 6])]
    status: TableStatusEnum = TableStatusEnum.available


class Table(TableBase, UUIDSchema, TimestampSchema):
    pass


class TableRead(TableBase):
    model_config = ConfigDict(from_attributes=True)
    section: SectionRead | None = None
    id: UUID


class TableCreate(TableBase):
    section_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])] | None = None
    model_config = ConfigDict(extra="forbid")


class TableCreateInternal(TableCreate):
    pass


class TableUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    number: Annotated[int, Field(gt=0, examples=[1, 2, 3])] | None = None
    capacity: Annotated[int, Field(gt=0, examples=[2, 4, 6])] | None = None
    status: TableStatusEnum | None = None
    section_id: Annotated[UUID, Field(examples=[UUID("12345678-1234-1234-1234-123456789012")])] | None = None


class TableUpdateInternal(TableUpdate):
    updated_at: datetime
