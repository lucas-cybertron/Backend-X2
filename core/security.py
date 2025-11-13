# core/security.py
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# ===========================================================
# 🔹 Carrega variáveis de ambiente
# ===========================================================
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret_key_development")  # deve ficar no .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # tempo padrão do token (1h)

# ===========================================================
# 🔹 Criptografia de senha
# ===========================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Cria um hash seguro da senha do usuário"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha digitada confere com o hash"""
    return pwd_context.verify(plain_password, hashed_password)

# ===========================================================
# 🔹 Token JWT
# ===========================================================
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Gera um token JWT com dados e tempo de expiração"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decodifica e valida um token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
