from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class LinkCreate(BaseModel):
    url: HttpUrl
    custom_alias: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=16,
        pattern=r"^[A-Za-z0-9_-]+$",
    )


class LinkResponse(BaseModel):
    code: str
    short_url: str
    target_url: str
    created_at: datetime
    total_clicks: int


class DailyClicks(BaseModel):
    date: str
    clicks: int


class StatsResponse(BaseModel):
    code: str
    total_clicks: int
    window_days: int
    by_day: list[DailyClicks]
