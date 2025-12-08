# Relatório de Análise — Backend X2 Futebol

Data: 2025-12-08

Resumo executivo
---------------
Projeto organizado em FastAPI + SQLAlchemy com separação clara entre `routers/`, `services/`, `models/` e `schemas/`. Implementação coerente e bem documentada. Há pontos de segurança, operação e robustez a ajustar antes de ir para produção.

Principais achados
------------------
- Estrutura do projeto: boa separação de responsabilidades.
- Autenticação: JWT com access/refresh tokens e hashing (`passlib` + `bcrypt`) está corretamente implementada.
- Banco: uso de SQLAlchemy com `Base.metadata.create_all(bind=engine)` (bom para dev, migrar para Alembic em produção).
- Dependências: `requirements.txt` contém uma entrada inválida `pydantic[email]` (ver correção abaixo).
- CORS configurado com `allow_origins=["*"]` — inseguro em produção.
- `core/security.py` falha na importação se `SECRET_KEY` não estiver definido — impede import em alguns contextos (scripts/testes).
- Algumas operações de DB não usam rollback em exceções — risco de transações parcialmente aplicadas.
- Nome de coluna `type` no modelo `User` (poderia conflitar semanticamente com built-in). Recomendo `role`.
- `services/partidas.py` regenera a tabela apagando tudo (`Tabela`), abordagem potencialmente pesada e com risco de concorrência.

Recomendações imediatas (correções mínimas que posso aplicar)
------------------------------------------------------------
1) Corrigir `requirements.txt`
   - Remover a linha `pydantic[email]` ou especificar corretamente.
   - Conteúdo recomendado (corrigido):

```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-jose[cryptography]==3.3.0
python-multipart>=0.0.7
numpy>=2.2.6
python-dotenv>=1.0.0
email-validator==1.4.0
passlib==1.7.4
bcrypt==4.1.2
```

2) Adicionar `.env.example`
   - Arquivo para documentar variáveis necessárias. Exemplo proposto:

```
# .env.example — não commit secrets reais
DATABASE_URL=sqlite:///./dev.db
SECRET_KEY=your-secure-secret-key
ALLOWED_ORIGINS=http://localhost:3000,https://meu-front.example
ENV=development
```

3) Tornar `CORS` configurável por variável de ambiente
   - Substituir `allow_origins=["*"]` por leitura de `ALLOWED_ORIGINS`:

```python
# no topo de main.py
from dotenv import load_dotenv
import os
load_dotenv()
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
if ALLOWED_ORIGINS:
    allowed_origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]
else:
    allowed_origins = ["*"]  # permit para dev, evite em produção

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

4) Ajuste em `core/security.py` para não quebrar import em ambientes sem `.env`
   - Recomendo falhar apenas em produção, ou documentar/usar valor default só para dev:

```python
SECRET_KEY = os.getenv("SECRET_KEY")
ENV = os.getenv("ENV", "development")
if not SECRET_KEY and ENV == "production":
    raise ValueError("SECRET_KEY não encontrada no arquivo .env — não rode em production sem ela")

# Para desenvolvimento, um fallback pode ser usado (não para produção):
if not SECRET_KEY:
    SECRET_KEY = "dev-secret-change-me"
```

5) Usar rollback em serviços que fazem múltiplas operações de DB
   - Exemplo (padrão para operações que `add` + `commit`):

```python
try:
    db.add(obj)
    db.commit()
    db.refresh(obj)
except Exception:
    db.rollback()
    raise
```

6) Migrar de `Base.metadata.create_all()` para Alembic em produção
   - `create_all` é útil em dev, mas para controle de schema em produção use Alembic.

7) Modelagem: renomear `User.type` para `User.role` (opcional)
   - Se decidir renomear, crie migração no Alembic. Justificativa: evita confusão com `type()` e deixa a intenção mais clara.

8) `services/partidas.py` — evitar apagar `Tabela` inteira frequentemente
   - Alternativas:
     - Calcular a tabela on-demand via consultas agregadas (mais seguro para concorrência).
     - Se persistir tabela, executar atualização incremental ou bloquear durante recomputação.

9) Testes automáticos
   - Adicionar testes unitários para `auth`, `partidas` (cálculo de tabela) e `tournament`. Recomendo `pytest` + `pytest-asyncio` e um SQLite temporário para fixtures.

Sugestões opcionais de melhoria
-------------------------------
- Validar URLs (`escudo`, `logo`) com `HttpUrl`/`AnyUrl` do Pydantic quando adequado.
- Usar `OAuth2PasswordBearer` do FastAPI para integração com docs (atualmente a extração de token manual funciona).
- Travar tamanhos de `String` no models (ex.: `String(255)` para email) para interoperabilidade com outros DBs.
- Controlar o `random` em `services/tournament.py` durante testes (aceitar seed opcional).

Fragmentos de código recomendados
---------------------------------
- `requirements.txt` (corrigido) — já mostrado acima.

- `.env.example` — já mostrado acima.

- Alteração simples em `core/security.py` (fallback dev + check em production):

```python
SECRET_KEY = os.getenv("SECRET_KEY")
ENV = os.getenv("ENV", "development")
if not SECRET_KEY and ENV == "production":
    raise ValueError("❌ SECRET_KEY não encontrada no arquivo .env — definir em production")
if not SECRET_KEY:
    SECRET_KEY = "dev-secret-not-for-production"
```

- Uso de rollback em serviços (exemplo genérico):

```python
def create_entity(data, db: Session):
    try:
        obj = Entity(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    except Exception:
        db.rollback()
        raise
```

- Leitura `ALLOWED_ORIGINS` em `main.py` (trecho acima).

Comandos úteis
--------------
- Criar virtualenv (Windows PowerShell):

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Rodar localmente:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Rodar testes (se implementados):

```powershell
pytest -q
```

Plano de ação sugerido (posso executar)
--------------------------------------
- A (correções imediatas): corrigir `requirements.txt`, adicionar `.env.example`, alterar `main.py` para ler `ALLOWED_ORIGINS` e ajustar `core/security.py` para não quebrar em dev.
- B (relatório): este arquivo — já gerado (`RELATORIO_ANALISE.md`).
- C (tests): criar testes unitários básicos para `auth` e `partidas`.

Você pediu a opção B — gerei este relatório detalhado em `RELATORIO_ANALISE.md`.

Próximo passo
-------------
- Posso aplicar as correções do item A agora (modificar `requirements.txt`, adicionar `.env.example`, e ajustar `main.py` e `core/security.py`) se desejar — responda `A` ou `A+C` para também criar testes.


---
Arquivo criado automaticamente pelo processo de revisão.
