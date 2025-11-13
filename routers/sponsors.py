# routers/sponsor.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.sponsor import SponsorCreate, SponsorUpdate, SponsorResponse
from services.sponsor_service import (
    create_sponsor,
    get_all_sponsors,
    get_sponsor_by_id,
    update_sponsor,
    delete_sponsor
)

router = APIRouter(prefix="/sponsors", tags=["Sponsors"])

@router.post("/", response_model=SponsorResponse)
def create_sponsor_route(sponsor: SponsorCreate, db: Session = Depends(get_db)):
    return create_sponsor(sponsor, db)

@router.get("/", response_model=list[SponsorResponse])
def list_sponsors_route(db: Session = Depends(get_db)):
    return get_all_sponsors(db)

@router.get("/{sponsor_id}", response_model=SponsorResponse)
def get_sponsor_route(sponsor_id: int, db: Session = Depends(get_db)):
    return get_sponsor_by_id(sponsor_id, db)

@router.put("/{sponsor_id}", response_model=SponsorResponse)
def update_sponsor_route(sponsor_id: int, sponsor: SponsorUpdate, db: Session = Depends(get_db)):
    return update_sponsor(sponsor_id, sponsor, db)

@router.delete("/{sponsor_id}")
def delete_sponsor_route(sponsor_id: int, db: Session = Depends(get_db)):
    return delete_sponsor(sponsor_id, db)
