# services/tournament_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.tournament import Tournament
from schemas.tournament import TournamentCreate, TournamentUpdate

def create_tournament(data: TournamentCreate, db: Session):
    """Cria um novo torneio."""
    existing = db.query(Tournament).filter(Tournament.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Torneio já existe.")

    tournament = Tournament(
        name=data.name,
        location=data.location,
        start_date=data.start_date,
        end_date=data.end_date,
        description=data.description
    )

    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    return tournament


def list_tournaments(db: Session):
    """Lista todos os torneios."""
    return db.query(Tournament).all()


def get_tournament_by_id(tournament_id: int, db: Session):
    """Busca torneio por ID."""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio não encontrado.")
    return tournament


def update_tournament(tournament_id: int, data: TournamentUpdate, db: Session):
    """Atualiza informações de um torneio."""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio não encontrado.")

    if data.name:
        tournament.name = data.name
    if data.location:
        tournament.location = data.location
    if data.start_date:
        tournament.start_date = data.start_date
    if data.end_date:
        tournament.end_date = data.end_date
    if data.description:
        tournament.description = data.description

    db.commit()
    db.refresh(tournament)
    return tournament


def delete_tournament(tournament_id: int, db: Session):
    """Remove um torneio."""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio não encontrado.")

    db.delete(tournament)
    db.commit()
    return {"message": "Torneio removido com sucesso."}
