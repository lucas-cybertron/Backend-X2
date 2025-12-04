from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.models import Patrocinadores
from schemas.schemas import (
    PatrocinadorCreate,
    PatrocinadorUpdate,
    PatrocinadorResponse,
)


# ===========================================================
# 🔹 SERVIÇOS DE PATROCINADORES
# ===========================================================


def create_patrocinador(patrocinador_data: PatrocinadorCreate, db: Session) -> PatrocinadorResponse:
    """
    Cria um novo patrocinador
    
    Args:
        patrocinador_data: Dados do patrocinador
        db: Sessão do banco de dados
        
    Returns:
        PatrocinadorResponse com dados do patrocinador
    """
    new_patrocinador = Patrocinadores(
        nome=patrocinador_data.nome,
        logo=patrocinador_data.logo,
    )

    db.add(new_patrocinador)
    db.commit()
    db.refresh(new_patrocinador)

    return PatrocinadorResponse.from_orm(new_patrocinador)


def get_all_patrocinadores(db: Session, skip: int = 0, limit: int = 100) -> list[PatrocinadorResponse]:
    """
    Lista todos os patrocinadores
    
    Args:
        db: Sessão do banco de dados
        skip: Número de registros a pular (paginação)
        limit: Número máximo de registros
        
    Returns:
        Lista de PatrocinadorResponse
    """
    patrocinadores = db.query(Patrocinadores).offset(skip).limit(limit).all()
    return [PatrocinadorResponse.from_orm(p) for p in patrocinadores]


def get_patrocinador_by_id(patrocinador_id: int, db: Session) -> PatrocinadorResponse:
    """
    Busca um patrocinador pelo ID
    
    Args:
        patrocinador_id: ID do patrocinador
        db: Sessão do banco de dados
        
    Returns:
        PatrocinadorResponse
        
    Raises:
        HTTPException: Se patrocinador não encontrado
    """
    patrocinador = db.query(Patrocinadores).filter(Patrocinadores.id == patrocinador_id).first()

    if not patrocinador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patrocinador não encontrado",
        )

    return PatrocinadorResponse.from_orm(patrocinador)


def update_patrocinador(patrocinador_id: int, patrocinador_data: PatrocinadorUpdate, db: Session) -> PatrocinadorResponse:
    """
    Atualiza dados de um patrocinador
    
    Args:
        patrocinador_id: ID do patrocinador
        patrocinador_data: Novos dados
        db: Sessão do banco de dados
        
    Returns:
        PatrocinadorResponse atualizado
        
    Raises:
        HTTPException: Se patrocinador não encontrado
    """
    patrocinador = db.query(Patrocinadores).filter(Patrocinadores.id == patrocinador_id).first()

    if not patrocinador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patrocinador não encontrado",
        )

    if patrocinador_data.nome:
        patrocinador.nome = patrocinador_data.nome
    if patrocinador_data.logo:
        patrocinador.logo = patrocinador_data.logo

    db.commit()
    db.refresh(patrocinador)

    return PatrocinadorResponse.from_orm(patrocinador)


def delete_patrocinador(patrocinador_id: int, db: Session) -> dict:
    """
    Deleta um patrocinador
    
    Args:
        patrocinador_id: ID do patrocinador
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se patrocinador não encontrado
    """
    patrocinador = db.query(Patrocinadores).filter(Patrocinadores.id == patrocinador_id).first()

    if not patrocinador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patrocinador não encontrado",
        )

    db.delete(patrocinador)
    db.commit()

    return {"message": "Patrocinador deletado com sucesso"}
