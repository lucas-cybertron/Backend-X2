from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from services.partidas import (
    create_partida,
    get_all_partidas,
    get_partida_by_id,
    update_partida,
    delete_partida,
    get_tabela,
    get_posicao_time,
)
from schemas.schemas import (
    PartidaCreate,
    PartidaUpdate,
    PartidaResponse,
    TabelaResponse,
)

# ===========================================================
# 🔹 Configuração do Router
# ===========================================================
router = APIRouter(
    prefix="/partidas",
    tags=["partidas"],
    responses={404: {"description": "Não encontrado"}},
)


# ===========================================================
# 🔹 ENDPOINTS DE PARTIDAS (HISTÓRICO)
# ===========================================================


@router.post("", response_model=PartidaResponse, status_code=status.HTTP_201_CREATED)
async def criar_partida(partida_data: PartidaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova partida e atualiza a tabela automaticamente
    
    - **time_mandante_id**: ID do time mandante
    - **time_visitante_id**: ID do time visitante
    - **data_hora**: Data e hora da partida (ISO format)
    - **local**: Local da partida
    - **placar_mandante**: Placar do time mandante
    - **placar_visitante**: Placar do time visitante
    """
    return create_partida(partida_data, db)


@router.get("", response_model=list[PartidaResponse])
async def listar_partidas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todas as partidas (histórico) ordenadas pela data mais recente
    
    - **skip**: Número de registros a pular (padrão: 0)
    - **limit**: Limite de registros (padrão: 100)
    """
    return get_all_partidas(db, skip, limit)


@router.get("/{partida_id}", response_model=PartidaResponse)
async def obter_partida(partida_id: int, db: Session = Depends(get_db)):
    """
    Obtém uma partida específica pelo ID
    """
    return get_partida_by_id(partida_id, db)


@router.put("/{partida_id}", response_model=PartidaResponse)
async def atualizar_partida(partida_id: int, partida_data: PartidaUpdate, db: Session = Depends(get_db)):
    """
    Atualiza o placar de uma partida e regenera a tabela automaticamente
    
    - **placar_mandante**: Novo placar do mandante (opcional)
    - **placar_visitante**: Novo placar do visitante (opcional)
    """
    return update_partida(partida_id, partida_data, db)


@router.delete("/{partida_id}")
async def deletar_partida(partida_id: int, db: Session = Depends(get_db)):
    """
    Deleta uma partida e regenera a tabela automaticamente
    """
    return delete_partida(partida_id, db)


# ===========================================================
# 🔹 ENDPOINTS DE TABELA DE CLASSIFICAÇÃO
# ===========================================================


@router.get("/tabela/classificacao", response_model=list[TabelaResponse])
async def obter_tabela(db: Session = Depends(get_db)):
    """
    Retorna a tabela de classificação atualizada automaticamente
    
    Informações retornadas:
    - **posicao**: Posição na tabela
    - **pontos**: Pontos totais (3 por vitória, 1 por empate)
    - **jogos**: Número de jogos disputados
    - **vitorias**: Número de vitórias
    - **empates**: Número de empates
    - **derrotas**: Número de derrotas
    - **gols_pro**: Gols marcados
    - **gols_contra**: Gols sofridos
    - **saldo_gols**: Diferença entre gols pro e contra
    """
    return get_tabela(db)


@router.get("/tabela/time/{time_id}", response_model=TabelaResponse)
async def obter_posicao_time(time_id: int, db: Session = Depends(get_db)):
    """
    Retorna a posição de um time específico na tabela
    """
    return get_posicao_time(time_id, db)
