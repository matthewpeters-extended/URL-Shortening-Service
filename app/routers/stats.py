from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Url
from app.schemas import UrlStatsOut
from app.short_code import decode, encode

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/{short_code}", response_model=UrlStatsOut)
def get_stats(short_code: str, db: Session = Depends(get_db)):
    try:
        url_id = decode(short_code)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Short URL not found")

    url = db.get(Url, url_id)
    if url is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Short URL not found")

    return UrlStatsOut(
        id=url.id,
        original_url=url.original_url,
        short_url=f"{settings.base_url}/shorten/{encode(url.id)}",
        created_at=url.created_at,
        usage_count=url.usage_count,
    )
