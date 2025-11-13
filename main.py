# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from routers import auth, teams, matches, sponsors, tournaments  # 👈 importa os 3 routers
from models import user, team as team_model, match as match_model  # garante criação das tabelas

# ===========================================================
# 🔹 Inicializa o app FastAPI
# ===========================================================
app = FastAPI(
    title="X2 Futebol API",
    description="Backend do sistema de gerenciamento e marketing dos jogos de futebol do projeto X2.",
    version="1.0.0",
)

# ===========================================================
# 🔹 Configuração do CORS (permite acesso do frontend)
# ===========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # futuramente pode limitar para o domínio do site (ex: ["https://x2.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================================================
# 🔹 Criação automática das tabelas
# ===========================================================
Base.metadata.create_all(bind=engine)

# ===========================================================
# 🔹 Registro dos routers
# ===========================================================
app.include_router(auth.router)    # Rotas de autenticação (/auth)
app.include_router(teams.router)    # Rotas de times (/teams)
app.include_router(matches.router)   # Rotas de partidas (/matches)
app.include_router(sponsors.router)
app.include_router(tournaments.router)

# ===========================================================
# 🔹 Rota inicial (teste)
# ===========================================================
@app.get("/")
def root():
    return {"message": "🚀 API X2 Futebol está online!"}
