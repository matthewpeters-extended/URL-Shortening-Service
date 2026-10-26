from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.limiter import limiter
from app.models import Url
from app.schemas import ShortenRequest, ShortenResponse
from app.short_code import decode, encode

router = APIRouter(prefix="/shorten", tags=["shorten"])


def _short_url_for(url: Url) -> str:
    return f"{settings.base_url}/shorten/{encode(url.id)}"


@router.post("", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def shorten_url(request: Request, payload: ShortenRequest, db: Session = Depends(get_db)):
    original_url = str(payload.originalUrl)

    # Shortening the same URL twice returns the existing short code rather
    # than minting a second one, so the table does not fill up with
    # duplicate rows pointing at the same destination.
    existing = db.query(Url).filter(Url.original_url == original_url).first()
    if existing is not None:
        return ShortenResponse(shortUrl=_short_url_for(existing))

    url = Url(original_url=original_url)
    db.add(url)
    db.commit()
    db.refresh(url)
    return ShortenResponse(shortUrl=_short_url_for(url))


@router.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    try:
        url_id = decode(short_code)
    except ValueError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Short URL not found")

    url = db.get(Url, url_id)
    if url is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Short URL not found")

    url.usage_count += 1
    db.commit()

    return RedirectResponse(url=url.original_url, status_code=status.HTTP_302_FOUND)
