from typing import List, Optional
import random
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.models import Time, TournamentBracket
from schemas.schemas import BracketPair
from fastapi import HTTPException
from sqlalchemy import func


def draw_bracket(team_ids: List[int], db: Optional[Session] = None, seeded: bool = False) -> List[BracketPair]:
    """
    Gera um chaveamento simples (pares) a partir de uma lista de IDs de times.
    - Se `seeded` for False (padrão), embaralha as equipes antes de gerar pares.
    - Se o número de times for ímpar, o último par terá `team_b_id = None` (bye).

    Se `db` for fornecido, valida se os time_ids existem no banco e retorna error 404 se algum não existir.
    """
    if not isinstance(team_ids, list) or len(team_ids) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="team_ids deve ser uma lista não vazia")

    # Validação opcional contra DB
    if db is not None:
        existing = {t.id for t in db.query(Time).filter(Time.id.in_(team_ids)).all()}
        missing = [tid for tid in team_ids if tid not in existing]
        if missing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Times não encontrados: {missing}")

    teams = team_ids.copy()
    if not seeded:
        random.shuffle(teams)

    pairs: List[BracketPair] = []
    # Se número ímpar, adiciona bye (None) na lista para facilitar pareamento
    if len(teams) % 2 == 1:
        teams.append(None)

    for i in range(0, len(teams), 2):
        a = teams[i]
        b = teams[i + 1] if i + 1 < len(teams) else None
        pairs.append(BracketPair(team_a_id=a, team_b_id=b))

    return pairs


def persist_bracket(tournament_name: str, team_ids: List[int], db: Session, seeded: bool = False):
    """
    Gera um chaveamento e persiste todos os pares na tabela `tournament_brackets`.
    """
    pairs = draw_bracket(team_ids, db=db, seeded=seeded)

    persisted_pairs = []
    match_number = 1
    for pair in pairs:
        # Resolve names (if available) to store denormalized names in DB
        team_a_name = None
        team_b_name = None
        if pair.team_a_id:
            t_a = db.query(Time).filter(Time.id == pair.team_a_id).first()
            team_a_name = t_a.nome if t_a else None
        if pair.team_b_id:
            t_b = db.query(Time).filter(Time.id == pair.team_b_id).first()
            team_b_name = t_b.nome if t_b else None

        bracket = TournamentBracket(
            tournament_name=tournament_name,
            round=1,
            match_number=match_number,
            team_a_id=pair.team_a_id,
            team_b_id=pair.team_b_id,
            team_a_name=team_a_name,
            team_b_name=team_b_name,
        )
        db.add(bracket)
        match_number += 1

    db.commit()

    persisted = db.query(TournamentBracket).filter(
        TournamentBracket.tournament_name == tournament_name
    ).all()

    result = []
    for bracket in persisted:
        result.append({
            'id': bracket.id,
            'team_a_id': bracket.team_a_id,
            'team_a_name': bracket.team_a_name,
            'team_b_id': bracket.team_b_id,
            'team_b_name': bracket.team_b_name,
            'winner_id': bracket.winner_id,
            'winner_name': bracket.winner_name,
        })

    return {
        'tournament_name': tournament_name,
        'pairs_count': len(result),
        'pairs': result,
    }


def list_brackets(tournament_name: Optional[str] = None, db: Optional[Session] = None):
    """
    Lista todos os chaveamentos, opcionalmente filtrado por nome do torneio.
    """
    if db is None:
        return []

    query = db.query(TournamentBracket)
    if tournament_name:
        query = query.filter(TournamentBracket.tournament_name == tournament_name)

    brackets = query.all()
    result = []
    for bracket in brackets:
        result.append({
            'id': bracket.id,
            'tournament_name': bracket.tournament_name,
            'round': bracket.round,
            'match_number': bracket.match_number,
            'team_a_id': bracket.team_a_id,
            'team_a_name': bracket.team_a_name,
            'team_b_id': bracket.team_b_id,
            'team_b_name': bracket.team_b_name,
            'winner_id': bracket.winner_id,
            'winner_name': bracket.winner_name,
        })

    return result


def set_match_result(bracket_id: int, score_a: int, score_b: int, db: Session):
    """Seta o placar de uma partida e define o vencedor automaticamente quando possível.
    Retorna o registro atualizado como dicionário.
    """
    bracket = db.query(TournamentBracket).filter(TournamentBracket.id == bracket_id).first()
    if not bracket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chaveamento não encontrado")

    bracket.team_a_score = score_a
    bracket.team_b_score = score_b

    if score_a is not None and score_b is not None:
        if score_a > score_b:
            bracket.winner_id = bracket.team_a_id
            bracket.winner_name = bracket.team_a_name
        elif score_b > score_a:
            bracket.winner_id = bracket.team_b_id
            bracket.winner_name = bracket.team_b_name
        else:
            # empate: não decide o vencedor automaticamente
            bracket.winner_id = None
            bracket.winner_name = None

    db.add(bracket)
    db.commit()
    db.refresh(bracket)

    return {
        'id': bracket.id,
        'tournament_name': bracket.tournament_name,
        'round': bracket.round,
        'match_number': bracket.match_number,
        'team_a_id': bracket.team_a_id,
        'team_a_name': bracket.team_a_name,
        'team_b_id': bracket.team_b_id,
        'team_b_name': bracket.team_b_name,
        'team_a_score': bracket.team_a_score,
        'team_b_score': bracket.team_b_score,
        'winner_id': bracket.winner_id,
        'winner_name': bracket.winner_name,
    }


def advance_round_if_ready(tournament_name: str, db: Session):
    """Se todos os jogos de uma rodada tiverem vencedores, cria a próxima rodada com os vencedores.
    Retorna um resumo indicando se avançou e quantas partidas foram criadas.
    """
    # Descobre a rodada atual máxima
    max_round = db.query(func.max(TournamentBracket.round)).filter(TournamentBracket.tournament_name == tournament_name).scalar()
    if not max_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum chaveamento encontrado para esse torneio")

    # Busca todas as partidas da rodada atual
    current = db.query(TournamentBracket).filter(
        TournamentBracket.tournament_name == tournament_name,
        TournamentBracket.round == max_round,
    ).order_by(TournamentBracket.match_number).all()

    if not current:
        return {'advanced': False, 'reason': 'No matches in current round'}

    # Verifica se todas têm winner_id
    if any([c.winner_id is None for c in current]):
        return {'advanced': False, 'reason': 'Not all matches have winners'}

    # Coleta vencedores em ordem
    winners = [(c.winner_id, c.winner_name) for c in current if c.winner_id]
    winner_ids = [w[0] for w in winners]
    winner_names = {w[0]: w[1] for w in winners}

    # Se apenas um vencedor, torneio acabou
    if len(winner_ids) <= 1:
        return {'advanced': False, 'reason': 'Tournament has a single winner already', 'winner': winners[0] if winners else None}

    # Se ímpar, adiciona bye
    if len(winner_ids) % 2 == 1:
        winner_ids.append(None)

    next_round = max_round + 1
    created = 0
    match_number = 1
    for i in range(0, len(winner_ids), 2):
        a = winner_ids[i]
        b = winner_ids[i + 1] if i + 1 < len(winner_ids) else None
        team_a_name = winner_names.get(a) if a else None
        team_b_name = winner_names.get(b) if b else None

        nb = TournamentBracket(
            tournament_name=tournament_name,
            round=next_round,
            match_number=match_number,
            team_a_id=a,
            team_b_id=b,
            team_a_name=team_a_name,
            team_b_name=team_b_name,
        )
        db.add(nb)
        created += 1
        match_number += 1

    db.commit()
    return {'advanced': True, 'next_round': next_round, 'pairs_created': created}
