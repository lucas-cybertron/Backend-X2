from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from services.patrocinadores import (
    create_patrocinador,
    get_all_patrocinadores,
    get_patrocinador_by_id,
    update_patrocinador,
    delete_patrocinador,
)
from schemas.schemas import (
    PatrocinadorCreate,
    PatrocinadorUpdate,
    PatrocinadorResponse,
)

# ===========================================================
# 🔹 Configuração do Router
# ===========================================================
router = APIRouter(
    prefix="/patrocinadores",
    tags=["patrocinadores"],
    responses={404: {"description": "Não encontrado"}},
)


# ===========================================================
# 🔹 ENDPOINTS DE PATROCINADORES
# ===========================================================


@router.post("", response_model=PatrocinadorResponse, status_code=status.HTTP_201_CREATED)
async def criar_patrocinador(patrocinador_data: PatrocinadorCreate, db: Session = Depends(get_db)):
    """
    Cria um novo patrocinador
    
    - **nome**: Nome do patrocinador
    - **logo**: URL da logo (opcional)
    """
    return create_patrocinador(patrocinador_data, db)


@router.get("", response_model=list[PatrocinadorResponse])
async def listar_patrocinadores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos os patrocinadores com paginação
    
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Limite de registros (padrão: 100)
    """
    return get_all_patrocinadores(db, skip, limit)


@router.get("/{patrocinador_id}", response_model=PatrocinadorResponse)
async def obter_patrocinador(patrocinador_id: int, db: Session = Depends(get_db)):
    """
    Obtém um patrocinador específico pelo ID
    """
    return get_patrocinador_by_id(patrocinador_id, db)


@router.put("/{patrocinador_id}", response_model=PatrocinadorResponse)
async def atualizar_patrocinador(patrocinador_id: int, patrocinador_data: PatrocinadorUpdate, db: Session = Depends(get_db)):
    """
    Atualiza dados de um patrocinador
    
    - **nome**: Novo nome (opcional)
    - **logo**: Nova logo (opcional)
    """
    return update_patrocinador(patrocinador_id, patrocinador_data, db)


@router.delete("/{patrocinador_id}")
async def deletar_patrocinador(patrocinador_id: int, db: Session = Depends(get_db)):
    """
    Deleta um patrocinador
    """
    return delete_patrocinador(patrocinador_id, db)
