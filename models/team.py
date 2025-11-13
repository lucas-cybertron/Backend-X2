# models/team.py
from sqlalchemy import Column, Integer, String, DateTime
from core.database import Base
from datetime import datetime, timezone

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    city = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
