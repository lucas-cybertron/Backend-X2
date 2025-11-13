# schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

# ===========================================================
# 🔹 Enum para tipos de usuário (igual ao do models.user)
# ===========================================================
class UserType(str, Enum):
    SUPERADM = "superadm"
    ADM = "adm"
    CLIENTE = "cliente"

# ===========================================================
# 🔹 Schemas de entrada e saída de dados
# ===========================================================

class UserBase(BaseModel):
    email: EmailStr
    type: UserType = UserType.CLIENTE  # padrão é cliente

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # permite converter automaticamente ORM → Pydantic

# ===========================================================
# 🔹 Schema para o token JWT
# ===========================================================
class Token(BaseModel):
    access_token: str
    token_type: str
