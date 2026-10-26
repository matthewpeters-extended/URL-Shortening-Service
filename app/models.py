from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    usage_count = Column(Integer, nullable=False, default=0)
