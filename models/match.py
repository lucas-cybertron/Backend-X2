# models/match.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    team_a_id = Column(Integer, ForeignKey("teams.id"))
    team_b_id = Column(Integer, ForeignKey("teams.id"))
    score_a = Column(Integer, default=0)
    score_b = Column(Integer, default=0)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    location = Column(String, nullable=True)

    team_a = relationship("Team", foreign_keys=[team_a_id])
    team_b = relationship("Team", foreign_keys=[team_b_id])
