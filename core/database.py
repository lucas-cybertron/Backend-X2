from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv  # <--- precisa disso
import os

# 🔹 Carrega as variáveis do arquivo .env
load_dotenv()

# 🔹 Agora ele vai encontrar o DATABASE_URL
SQLITE_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLITE_DATABASE_URL:
    raise ValueError("❌ DATABASE_URL não encontrada no arquivo .env")

# 🔹 Cria o engine SQLite
engine = create_engine(
    SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
