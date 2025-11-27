# test_backend.py (corrigido)
from sqlalchemy.orm import Session
from core.database import Base, engine
from models.user import UserType
from services.team_service import create_team, get_all_teams
from services.match_service import create_match, list_matches
from services.sponsor_service import create_sponsor, get_all_sponsors
from services.tournament_service import create_tournament, list_tournaments
from services.auth_service import create_user
from schemas.user import UserCreate
from schemas.team import TeamCreate
from schemas.tournament import TournamentCreate
from schemas.sponsor import SponsorCreate
from schemas.match import MatchCreate
from datetime import datetime, date

# ==============================================
# Cria todas as tabelas
# ==============================================
Base.metadata.drop_all(bind=engine)  # Limpa tudo (opcional)
Base.metadata.create_all(bind=engine)

# ==============================================
# Sessão de banco
# ==============================================
db = Session(bind=engine)


# ==============================================
# Teste de Usuários
# ==============================================
print("===== Criando Usuários =====")
user1 = create_user(
    UserCreate(
        email="superadm@test.com",
        password="123",
        user_type=UserType.SUPERADM,
    ),
    db,
)
user2 = create_user(
    UserCreate(
        email="adm@test.com",
        password="123",
        user_type=UserType.ADM,
    ),
    db,
)
print("Usuários criados:", user1.email, user2.email)


# ==============================================
# Teste de Times
# ==============================================
print("\n===== Criando Times =====")
team1 = create_team(TeamCreate(name="Flamengo", city="Rio de Janeiro", logo_url=None), db)
team2 = create_team(TeamCreate(name="Palmeiras", city="São Paulo", logo_url=None), db)
print("Times criados:", team1.name, team2.name)


# ==============================================
# Teste de Torneios
# ==============================================
print("\n===== Criando Torneios =====")
tournament1 = create_tournament(
    TournamentCreate(
        name="Copa X2 2025",
        location="Brasil",
        start_date=date(2025, 11, 20),
        end_date=date(2025, 12, 20),
        description="Torneio teste do X2",
    ),
    db,
)
print("Torneio criado:", tournament1.name)


# ==============================================
# Teste de Patrocinadores
# ==============================================
print("\n===== Criando Patrocinadores =====")
sponsor1 = create_sponsor(
    SponsorCreate(
        name="Nike",
        logo_url=None,
        description="Marca esportiva",
        website="https://nike.com",
    ),
    db,
)
sponsor2 = create_sponsor(
    SponsorCreate(
        name="Adidas",
        logo_url=None,
        description="Marca esportiva",
        website="https://adidas.com",
    ),
    db,
)
print("Patrocinadores criados:", sponsor1.name, sponsor2.name)


# ==============================================
# Teste de Partidas
# ==============================================
print("\n===== Criando Partidas =====")
match1 = create_match(
    MatchCreate(
        team1_id=team1.id,
        team2_id=team2.id,
        location="Maracanã",
        date=datetime(2025, 11, 25, 16, 0),
    ),
    db,
)
print("Partida criada:", f"{team1.name} x {team2.name} em {match1.location} às {match1.date}")


# ==============================================
# Listagem Final para Validação
# ==============================================
print("\n===== Listagem de Times =====")
for t in get_all_teams(db):
    print(f"- {t.id}: {t.name} ({t.city})")

print("\n===== Listagem de Partidas =====")
for m in list_matches(db):
    print(f"- {m.id}: {m.team1.name} x {m.team2.name} ({m.date})")

print("\n===== Listagem de Torneios =====")
for t in list_tournaments(db):
    print(f"- {t.id}: {t.name} ({t.start_date} - {t.end_date})")

print("\n===== Listagem de Patrocinadores =====")
for s in get_all_sponsors(db):
    print(f"- {s.id}: {s.name} ({s.website})")

print("\n===== TODOS OS TESTES CONCLUÍDOS =====")
