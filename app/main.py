from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app import models  # noqa: F401  (import so Base knows about the tables)
from app.database import Base, engine
from app.limiter import limiter
from app.routers import shorten, stats

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortening Service")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(shorten.router)
app.include_router(stats.router)


@app.get("/health")
def health():
    return {"status": "ok"}
