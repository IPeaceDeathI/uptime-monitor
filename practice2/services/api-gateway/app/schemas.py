from datetime import datetime

from pydantic import BaseModel, Field


class SiteCreate(BaseModel):
    url: str = Field(..., max_length=2048)
    name: str = Field("", max_length=255)
    interval_sec: int = Field(60, ge=5, le=86400)


class SiteRead(BaseModel):
    id: int
    url: str
    name: str
    interval_sec: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CheckResultRead(BaseModel):
    id: int
    site_id: int
    status_code: int | None
    latency_ms: int | None
    is_up: bool
    checked_at: datetime

    model_config = {"from_attributes": True}


class SubscriberCreate(BaseModel):
    telegram_chat_id: str = Field(..., max_length=64)
    site_id: int | None = None


class SubscriberRead(BaseModel):
    id: int
    telegram_chat_id: str
    site_id: int | None

    model_config = {"from_attributes": True}
