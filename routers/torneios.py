from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from services.tournament import draw_bracket, persist_bracket, list_brackets
from schemas.schemas import TournamentDrawRequest, BracketResponse, BracketPersistRequest, BracketPersistResponse, BracketListResponse, BracketDetailResponse
from schemas.schemas import BracketItem
from services.tournament import set_match_result, advance_round_if_ready
from schemas.schemas import BracketItem
from pydantic import BaseModel


class MatchResultRequest(BaseModel):
    team_a_score: int
    team_b_score: int

router = APIRouter(
    prefix="/torneios",
    tags=["torneios"],
    responses={404: {"description": "Não encontrado"}},
)


@router.post("/sorteio", response_model=BracketResponse)
async def sorteio_chaveamento(data: TournamentDrawRequest, db: Session = Depends(get_db)):
    """
    Faz o sorteio dos times para um chaveamento de torneio (sem persistência).
    - `team_ids`: lista de IDs dos times participantes
    - `seeded`: se True, não embaralha, apenas cria pares pela ordem
    """
    pairs = draw_bracket(data.team_ids, db=db, seeded=data.seeded)
    return {"pairs": pairs}


@router.post("/sorteio/persist", response_model=BracketPersistResponse)
async def sorteio_e_persistir(data: BracketPersistRequest, db: Session = Depends(get_db)):
    """
    Faz o sorteio dos times e persiste os pares na tabela `tournament_brackets`.
    - `tournament_name`: nome do torneio
    - `team_ids`: lista de IDs dos times participantes
    - `seeded`: se True, não embaralha, apenas cria pares pela ordem
    """
    result = persist_bracket(data.tournament_name, data.team_ids, db, seeded=data.seeded)
    return BracketPersistResponse(
        tournament_name=result['tournament_name'],
        pairs_count=result['pairs_count'],
        pairs=result['pairs']
    )


@router.put('/chaveamentos/{bracket_id}/resultado', response_model=BracketDetailResponse)
async def set_result(bracket_id: int, body: MatchResultRequest, db: Session = Depends(get_db)):
    """Define o placar de uma partida. Se houver vencedor pelo placar, ele será definido automaticamente."""
    res = set_match_result(bracket_id, body.team_a_score, body.team_b_score, db)
    return BracketDetailResponse(**res)


@router.post('/chaveamentos/{tournament_name}/advance')
async def advance_tournament(tournament_name: str, db: Session = Depends(get_db)):
    """Avança o torneio para a próxima rodada se todos os jogos da rodada atual tiverem vencedores."""
    res = advance_round_if_ready(tournament_name, db)
    return res


@router.get("/chaveamentos", response_model=BracketListResponse)
async def listar_chaveamentos(tournament_name: str = None, db: Session = Depends(get_db)):
    """
    Lista todos os chaveamentos persistidos.
    - `tournament_name`: opcional, filtra por nome do torneio
    """
    brackets = list_brackets(tournament_name=tournament_name, db=db)
    items = [BracketDetailResponse(**bracket) for bracket in brackets]
    return BracketListResponse(total=len(items), items=items)


@router.get("/chaveamentos/{tournament_name}", response_model=BracketListResponse)
async def listar_chaveamentos_por_nome(tournament_name: str, db: Session = Depends(get_db)):
    """
    Lista todos os pares de um torneio específico.
    """
    brackets = list_brackets(tournament_name=tournament_name, db=db)
    items = [BracketDetailResponse(**bracket) for bracket in brackets]
    return BracketListResponse(total=len(items), items=items)
