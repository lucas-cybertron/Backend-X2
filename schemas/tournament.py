# schemas/tournament.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class TournamentBase(BaseModel):
    name: str
    location: str
    start_date: date
    end_date: date
    description: Optional[str] = None

class TournamentCreate(TournamentBase):
    pass

class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

class TournamentResponse(TournamentBase):
    id: int

    class Config:
        orm_mode = True
