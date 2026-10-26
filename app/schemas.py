from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel


class ShortenRequest(BaseModel):
    """Field is camelCase to match the task spec's exact request body
    (`{"originalUrl": "..."}`) rather than Python's usual snake_case."""

    originalUrl: AnyHttpUrl


class ShortenResponse(BaseModel):
    """Field is camelCase to match the task spec's exact response body
    (`{"shortUrl": "..."}`)."""

    shortUrl: str


class UrlStatsOut(BaseModel):
    id: int
    original_url: str
    short_url: str
    created_at: datetime
    usage_count: int
