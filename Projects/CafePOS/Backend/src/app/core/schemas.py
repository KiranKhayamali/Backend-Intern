from pydantic import BaseModel, Field, field_serializer
from datetime import datetime, timezone
from typing import Any

import uuid as uuid_pkg
from uuid6 import uuid7


class HealthCheck(BaseModel):
    status: str = Field(default="healthy")
    environment: str = Field(default="development")
    version: str = Field(default="latest", description="API version")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UUIDSchema(BaseModel):
    id: uuid_pkg.UUID = Field(default_factory=uuid7)


class TimestampSchema(BaseModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at: datetime | None = Field(default=None)

    @field_serializer("created_at")
    def serialize_dt(self, created_at: datetime | None, _info: Any) -> str | None:
        if created_at is not None:
            return created_at.isoformat()

        return None

    @field_serializer("updated_at")
    def serialize_updated_at(
        self, updated_at: datetime | None, _info: Any
    ) -> str | None:
        if updated_at is not None:
            return updated_at.isoformat()

        return None


class Token(BaseModel):
    access_token: str
    token_type: str
    expire_at: datetime


class LoginData(BaseModel):
    contact_number: str
    password: str
