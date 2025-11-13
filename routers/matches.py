# routers/match.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.match import Match
from schemas.match import MatchCreate, MatchResponse

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/", response_model=MatchResponse)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    """Cria uma nova partida"""
    new_match = Match(**match.dict())
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match

@router.get("/", response_model=list[MatchResponse])
def list_matches(db: Session = Depends(get_db)):
    """Lista todas as partidas"""
    return db.query(Match).all()
