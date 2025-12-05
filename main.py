# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from routers import auth, times, partidas, patrocinadores, torneios
from models.models import User  # garante criação das tabelas

# ===========================================================
# 🔹 Inicializa o app FastAPI
# ===========================================================
app = FastAPI(
    title="X2 Futebol API",
    description="Backend do sistema de gerenciamento e marketing dos jogos de futebol do projeto X2.",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,  # Mantém token salvo no Swagger
    },
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False
    }
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
app.include_router(auth.router)           # Rotas de autenticação (/auth)
app.include_router(times.router)          # Rotas de times (/times)
app.include_router(partidas.router)       # Rotas de partidas (/partidas)
app.include_router(patrocinadores.router) # Rotas de patrocinadores (/patrocinadores)
app.include_router(torneios.router)      # Rotas de torneios (/torneios)


# ===========================================================
# 🔹 Configuração de Segurança do Swagger
# ===========================================================
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="X2 Futebol API",
        version="1.0.0",
        description="Backend do sistema de gerenciamento e marketing dos jogos de futebol do projeto X2.",
        routes=app.routes,
    )
    
    # Adiciona configuração de segurança Bearer Token
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Insira seu token JWT aqui. Você pode obter um token fazendo login em `/auth/login`"
        }
    }
    # Aplica o esquema Bearer globalmente (mostra o cadeado e o header é enviado nas requests)
    openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# ===========================================================
# 🔹 Rota inicial (teste)
# ===========================================================
@app.get("/")
def root():
    return {"message": "🚀 API X2 Futebol está online!"}
