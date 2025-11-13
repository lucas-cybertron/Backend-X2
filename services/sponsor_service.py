# services/sponsor_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.sponsor import Sponsor
from schemas.sponsor import SponsorCreate, SponsorUpdate

def create_sponsor(sponsor_data: SponsorCreate, db: Session):
    """Cria um novo patrocinador."""
    existing = db.query(Sponsor).filter(Sponsor.name == sponsor_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esse patrocinador já existe."
        )

    sponsor = Sponsor(
        name=sponsor_data.name,
        logo_url=sponsor_data.logo_url,
        description=sponsor_data.description,
        website=sponsor_data.website
    )

    db.add(sponsor)
    db.commit()
    db.refresh(sponsor)
    return sponsor


def get_all_sponsors(db: Session):
    """Lista todos os patrocinadores."""
    return db.query(Sponsor).all()


def get_sponsor_by_id(sponsor_id: int, db: Session):
    """Retorna um patrocinador específico."""
    sponsor = db.query(Sponsor).filter(Sponsor.id == sponsor_id).first()
    if not sponsor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patrocinador não encontrado."
        )
    return sponsor


def update_sponsor(sponsor_id: int, sponsor_data: SponsorUpdate, db: Session):
    """Atualiza os dados de um patrocinador."""
    sponsor = db.query(Sponsor).filter(Sponsor.id == sponsor_id).first()
    if not sponsor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patrocinador não encontrado."
        )

    if sponsor_data.name:
        sponsor.name = sponsor_data.name
    if sponsor_data.logo_url:
        sponsor.logo_url = sponsor_data.logo_url
    if sponsor_data.description:
        sponsor.description = sponsor_data.description
    if sponsor_data.website:
        sponsor.website = sponsor_data.website

    db.commit()
    db.refresh(sponsor)
    return sponsor


def delete_sponsor(sponsor_id: int, db: Session):
    """Remove um patrocinador."""
    sponsor = db.query(Sponsor).filter(Sponsor.id == sponsor_id).first()
    if not sponsor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patrocinador não encontrado."
        )

    db.delete(sponsor)
    db.commit()
    return {"message": "Patrocinador removido com sucesso"}
