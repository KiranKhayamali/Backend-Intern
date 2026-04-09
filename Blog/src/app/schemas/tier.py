from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from ..core.schemas import TimestampSchema


class TierBase(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=100)]
    price: float


class Tier(TierBase, TimestampSchema):
    pass 


class TierRead(Tier):
    id: int 
    created_at: datetime


class TierCreate(TierBase):
    pass


class TierCreateInternal(TierBase):
    pass


class TierUpdate(BaseModel):
    name: str | None = None 


class TierUpdateInternal(TierUpdate):
    updated_at: datetime    


class TierDelete(BaseModel):
    pass