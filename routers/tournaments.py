# routers/tournament.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.tournament import TournamentCreate, TournamentUpdate, TournamentResponse
from services.tournament_service import (
    create_tournament,
    list_tournaments,
    get_tournament_by_id,
    update_tournament,
    delete_tournament
)

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])

@router.post("/", response_model=TournamentResponse)
def create_tournament_route(tournament: TournamentCreate, db: Session = Depends(get_db)):
    return create_tournament(tournament, db)

@router.get("/", response_model=list[TournamentResponse])
def list_tournaments_route(db: Session = Depends(get_db)):
    return list_tournaments(db)

@router.get("/{tournament_id}", response_model=TournamentResponse)
def get_tournament_route(tournament_id: int, db: Session = Depends(get_db)):
    return get_tournament_by_id(tournament_id, db)

@router.put("/{tournament_id}", response_model=TournamentResponse)
def update_tournament_route(tournament_id: int, tournament: TournamentUpdate, db: Session = Depends(get_db)):
    return update_tournament(tournament_id, tournament, db)

@router.delete("/{tournament_id}")
def delete_tournament_route(tournament_id: int, db: Session = Depends(get_db)):
    return delete_tournament(tournament_id, db)
