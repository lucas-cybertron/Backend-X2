# routers/team.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.team import Team
from schemas.team import TeamCreate, TeamResponse

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post("/", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    """Cria um novo time"""
    existing_team = db.query(Team).filter(Team.name == team.name).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Time já existe")

    new_team = Team(name=team.name, city=team.city)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team

@router.get("/", response_model=list[TeamResponse])
def list_teams(db: Session = Depends(get_db)):
    """Lista todos os times"""
    return db.query(Team).all()
