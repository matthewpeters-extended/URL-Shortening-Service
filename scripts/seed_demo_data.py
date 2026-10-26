"""One-off: shorten a couple of sample URLs so there is something to look
up via GET /shorten/{code} and GET /stats/{code} right after the server
starts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base, SessionLocal, engine
from app.models import Url
from app.short_code import encode

Base.metadata.create_all(bind=engine)

db = SessionLocal()

sample_urls = [
    "https://docs.anthropic.com/en/docs/claude-code",
    "https://fastapi.tiangolo.com/",
]

for original_url in sample_urls:
    existing = db.query(Url).filter(Url.original_url == original_url).first()
    if existing:
        print(f"Already shortened: {original_url} -> code {encode(existing.id)}")
        continue

    url = Url(original_url=original_url)
    db.add(url)
    db.commit()
    db.refresh(url)
    print(f"Shortened: {original_url} -> code {encode(url.id)}")

db.close()
