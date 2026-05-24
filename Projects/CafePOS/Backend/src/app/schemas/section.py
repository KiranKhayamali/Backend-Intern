from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID

from ..core.schemas import TimestampSchema, UUIDSchema


class SectionBase(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50, examples=["Rooftop", "Garden", "First Floor"])]


class Section(SectionBase, UUIDSchema, TimestampSchema):
    pass


class SectionRead(SectionBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID


class SectionCreate(SectionBase):
    model_config = ConfigDict(extra="forbid")


class SectionCreateInternal(SectionCreate):
    pass


class SectionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=3, max_length=50, examples=["Rooftop", "Garden", "First Floor"])] | None = None


class SectionUpdateInternal(SectionUpdate):
    updated_at: datetime
