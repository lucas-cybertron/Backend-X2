from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from services.times import (
    create_time,
    get_all_times,
    get_time_by_id,
    update_time,
    delete_time,
    create_jogador,
    get_jogadores_by_time,
    update_jogador,
    delete_jogador,
)
from schemas.schemas import (
    TimeCreate,
    TimeUpdate,
    TimeResponse,
    JogadorCreate,
    JogadorUpdate,
    JogadorResponse,
)

# ===========================================================
# 🔹 Configuração do Router
# ===========================================================
router = APIRouter(
    prefix="/times",
    tags=["times"],
    responses={404: {"description": "Não encontrado"}},
)


# ===========================================================
# 🔹 ENDPOINTS DE TIMES
# ===========================================================


@router.post("", response_model=TimeResponse, status_code=status.HTTP_201_CREATED)
async def create_novo_time(time_data: TimeCreate, db: Session = Depends(get_db)):
    """
    Cria um novo time
    
    - **nome**: Nome do time (obrigatório)
    - **escudo**: URL do escudo/logo (opcional)
    """
    return create_time(time_data, db)


@router.get("", response_model=list[TimeResponse])
async def listar_times(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos os times com paginação
    
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Limite de registros (padrão: 100)
    """
    return get_all_times(db, skip, limit)


@router.get("/{time_id}", response_model=TimeResponse)
async def obter_time(time_id: int, db: Session = Depends(get_db)):
    """
    Obtém um time específico pelo ID
    """
    return get_time_by_id(time_id, db)


@router.put("/{time_id}", response_model=TimeResponse)
async def atualizar_time(time_id: int, time_data: TimeUpdate, db: Session = Depends(get_db)):
    """
    Atualiza dados de um time
    
    - **nome**: Novo nome (opcional)
    - **escudo**: Novo escudo/logo (opcional)
    """
    return update_time(time_id, time_data, db)


@router.delete("/{time_id}")
async def deletar_time(time_id: int, db: Session = Depends(get_db)):
    """
    Deleta um time
    """
    return delete_time(time_id, db)


# ===========================================================
# 🔹 ENDPOINTS DE JOGADORES
# ===========================================================


@router.post("/{time_id}/jogadores", response_model=JogadorResponse, status_code=status.HTTP_201_CREATED)
async def criar_jogador(time_id: int, jogador_data: JogadorCreate, db: Session = Depends(get_db)):
    """
    Cria um novo jogador em um time
    
    - **nome**: Nome do jogador
    - **data_nascimento**: Data de nascimento (YYYY-MM-DD)
    - **time_id**: ID do time (será preenchido automaticamente da URL)
    """
    # Sobrescreve o time_id com o da URL
    jogador_data.time_id = time_id
    return create_jogador(jogador_data, db)


@router.get("/{time_id}/jogadores", response_model=list[JogadorResponse])
async def listar_jogadores_time(time_id: int, db: Session = Depends(get_db)):
    """
    Lista todos os jogadores de um time
    """
    return get_jogadores_by_time(time_id, db)


@router.put("/jogadores/{jogador_id}", response_model=JogadorResponse)
async def atualizar_jogador(jogador_id: int, jogador_data: JogadorUpdate, db: Session = Depends(get_db)):
    """
    Atualiza dados de um jogador
    
    - **nome**: Novo nome (opcional)
    - **data_nascimento**: Nova data de nascimento (opcional)
    """
    return update_jogador(jogador_id, jogador_data, db)


@router.delete("/jogadores/{jogador_id}")
async def deletar_jogador(jogador_id: int, db: Session = Depends(get_db)):
    """
    Deleta um jogador
    """
    return delete_jogador(jogador_id, db)
