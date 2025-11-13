# services/team_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.team import Team
from schemas.team import TeamCreate, TeamUpdate

def create_team(team_data: TeamCreate, db: Session):
    """
    Cria um novo time no banco de dados.
    """
    existing_team = db.query(Team).filter(Team.name == team_data.name).first()
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esse time já existe."
        )

    new_team = Team(
        name=team_data.name,
        city=team_data.city,
        logo_url=team_data.logo_url
    )

    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team


def get_all_teams(db: Session):
    """
    Retorna a lista de todos os times.
    """
    return db.query(Team).all()


def get_team_by_id(team_id: int, db: Session):
    """
    Retorna um time específico pelo ID.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado."
        )
    return team


def update_team(team_id: int, team_data: TeamUpdate, db: Session):
    """
    Atualiza as informações de um time existente.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado."
        )

    if team_data.name:
        team.name = team_data.name
    if team_data.city:
        team.city = team_data.city
    if team_data.logo_url:
        team.logo_url = team_data.logo_url

    db.commit()
    db.refresh(team)
    return team


def delete_team(team_id: int, db: Session):
    """
    Remove um time do banco de dados.
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado."
        )

    db.delete(team)
    db.commit()
    return {"message": "Time removido com sucesso"}
