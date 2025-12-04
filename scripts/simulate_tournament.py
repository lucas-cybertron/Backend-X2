"""Simula um torneio: persiste um chaveamento e define vencedores aleatórios.

Uso:
  - No PowerShell (usa o DB de teste gerado pelos testes):

    $env:DATABASE_URL='sqlite:///./test_complete_integration.db'; \
    .\venv\Scripts\python.exe scripts\simulate_tournament.py --tournament "Copa Simulada"

Se `DATABASE_URL` não apontar para um DB existente, o script criará times de exemplo.
"""
from typing import List
import random
import os
import argparse
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is on sys.path so imports work when running this script directly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.models import Base, Time, TournamentBracket
from services.tournament import persist_bracket, list_brackets, set_match_result, advance_round_if_ready


def get_db_session(database_url: str):
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Garantir que as tabelas existam
    Base.metadata.create_all(bind=engine)
    return Session()


def ensure_sample_teams(session, min_teams=4) -> List[int]:
    teams = session.query(Time).all()
    if len(teams) >= min_teams:
        return [t.id for t in teams]

    sample_names = ['Alpha FC', 'Beta United', 'Gamma Rovers', 'Delta City']
    created = []
    for name in sample_names:
        t = Time(nome=name)
        session.add(t)
        created.append(t)
    session.commit()
    return [t.id for t in session.query(Time).all()]


def simulate(tournament_name: str, db_url: str):
    print(f"Using DB: {db_url}")
    session = get_db_session(db_url)

    # Pegar ou criar times
    team_ids = ensure_sample_teams(session)
    print(f"Teams available: {team_ids}")

    # Persistir chaveamento
    result = persist_bracket(tournament_name, team_ids, session, seeded=False)
    print(f"Persisted pairs: {result['pairs_count']}")

    # Buscar pares persistidos da base
    brackets = session.query(TournamentBracket).filter(TournamentBracket.tournament_name == tournament_name).all()

    # Para cada par, escolher vencedor aleatório (ou dar bye quando team_b é None)
    # Para cada par vamos definir placares aleatórios e então tentar avançar a próxima rodada
    for b in brackets:
        if b.team_b_id is None:
            # bye -> team A gana com placar padrao
            set_match_result(b.id, 1, 0, session)
        else:
            a_score = random.randint(0, 3)
            b_score = random.randint(0, 3)
            set_match_result(b.id, a_score, b_score, session)

    # Tentar avançar automaticamente enquanto possível
    while True:
        adv = advance_round_if_ready(tournament_name, session)
        print(f"Advance attempt: {adv}")
        if not adv.get('advanced'):
            break
        # criar novos pares e então definir resultados aleatórios para a próxima rodada
        new_brackets = session.query(TournamentBracket).filter(TournamentBracket.tournament_name == tournament_name, TournamentBracket.round == adv['next_round']).all()
        for nb in new_brackets:
            if nb.team_b_id is None:
                set_match_result(nb.id, 1, 0, session)
            else:
                set_match_result(nb.id, random.randint(0,3), random.randint(0,3), session)

    # Mostrar resultados finais
    print('\n--- Tournament Results ---')
    updated = session.query(TournamentBracket).filter(TournamentBracket.tournament_name == tournament_name).order_by(TournamentBracket.round, TournamentBracket.match_number).all()
    for b in updated:
        a_name = b.team_a_name or f"(id:{b.team_a_id})"
        b_name = b.team_b_name or "(bye)"
        a_score = b.team_a_score if b.team_a_score is not None else '-'
        b_score = b.team_b_score if b.team_b_score is not None else '-'
        w_name = b.winner_name or '(none)'
        print(f"Round {b.round} Match {b.match_number}: {a_name} ({a_score}) vs {b_name} ({b_score}) -> Winner: {w_name}")

    session.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tournament', '-t', default='Copa Simulada', help='Nome do torneio')
    parser.add_argument('--db', '-d', default=None, help='Database URL (opcional)')
    args = parser.parse_args()

    db_url = args.db or os.getenv('DATABASE_URL') or 'sqlite:///./test_complete_integration.db'
    simulate(args.tournament, db_url)
