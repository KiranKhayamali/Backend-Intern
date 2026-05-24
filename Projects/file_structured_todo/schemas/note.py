from pydantic import BaseModel
from datetime import datetime


class NoteBase(BaseModel):
    title: str
    memo: str

    model_config = {
        "from_attributes": True
    }


class NoteSchema(NoteBase):
    id: int | None = None
    user_id: int | None = None


class NoteRead(NoteSchema):
    model_config = {
        "from_attributes": True
    }


class NoteCreate(NoteBase):
    model_config = {
        "extra": "forbid"
    }


class NoteCreateInternal(NoteCreate):
    created_at: datetime | None = None


class NoteUpdate(BaseModel):
    title: str | None = None
    memo: str | None = None

    model_config = {
        "extra": "forbid"
    }


class NoteUpdateInternal(NoteUpdate):
    updated_at: datetime | None = None
