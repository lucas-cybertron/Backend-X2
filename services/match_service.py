# services/match_service.py
from sqlalchemy.orm import Session
from models.match import Match
from models.team import Team
from schemas.match import MatchCreate
from fastapi import HTTPException, status
from datetime import datetime

def create_match(match_data: MatchCreate, db: Session):
    """
    Cria uma nova partida entre dois times.
    """
    # Verifica se os times existem
    team1 = db.query(Team).filter(Team.id == match_data.team1_id).first()
    team2 = db.query(Team).filter(Team.id == match_data.team2_id).first()

    if not team1 or not team2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Um ou ambos os times não foram encontrados."
        )

    if team1.id == team2.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uma partida precisa de dois times diferentes."
        )

    # Cria a partida
    new_match = Match(
        team1_id=team1.id,
        team2_id=team2.id,
        date=match_data.date or datetime.utcnow(),
        location=match_data.location,
        score_team1=None,
        score_team2=None
    )

    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


def update_match_result(match_id: int, score_team1: int, score_team2: int, db: Session):
    """
    Atualiza o placar de uma partida existente.
    """
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida não encontrada."
        )

    match.score_team1 = score_team1
    match.score_team2 = score_team2
    db.commit()
    db.refresh(match)
    return match


def list_matches(db: Session):
    """
    Lista todas as partidas.
    """
    return db.query(Match).all()
