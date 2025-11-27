# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from routers import auth
from models.models import User  # garante criação das tabelas

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


# ===========================================================
# 🔹 Rota inicial (teste)
# ===========================================================
@app.get("/")
def root():
    return {"message": "🚀 API X2 Futebol está online!"}
