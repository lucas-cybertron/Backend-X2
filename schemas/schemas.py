from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# =======================
# USER
# =======================
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    type: Optional[UserRole] = UserRole.USER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    type: Optional[UserRole] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =======================
# AUTH
# =======================
class UserRegister(BaseModel):
    """Schema para registro de novo usuário"""
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """Schema para login do usuário"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema para resposta com token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema para refresh de token"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Schema para mudar senha"""
    current_password: str
    new_password: str


# =======================
# JOGADORES
# =======================
class JogadorBase(BaseModel):
    nome: str
    data_nascimento: date
    time_id: int

class JogadorCreate(JogadorBase):
    pass

class JogadorUpdate(BaseModel):
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    time_id: Optional[int] = None

class JogadorResponse(JogadorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =======================
# TIME
# =======================
class TimeBase(BaseModel):
    nome: str
    escudo: Optional[str] = None

class TimeCreate(TimeBase):
    pass

class TimeUpdate(BaseModel):
    nome: Optional[str] = None
    escudo: Optional[str] = None

class TimeResponse(TimeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    jogadores: List[JogadorResponse] = []  # retorna jogadores do time

    class Config:
        from_attributes = True


# =======================
# PARTIDA
# =======================
class PartidaBase(BaseModel):
    data_hora: datetime
    local: str
    time_mandante_id: int
    time_visitante_id: int

class PartidaCreate(PartidaBase):
    pass

class PartidaUpdate(BaseModel):
    placar_mandante: Optional[int] = None
    placar_visitante: Optional[int] = None

class PartidaResponse(PartidaBase):
    id: int
    placar_mandante: int
    placar_visitante: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =======================
# TABELA
# =======================
class TabelaBase(BaseModel):
    posicao: int
    pontos: int
    jogos: int
    vitorias: int
    empates: int
    derrotas: int
    gols_pro: int
    gols_contra: int
    saldo_gols: int
    time_id: int

class TabelaCreate(TabelaBase):
    pass

class TabelaUpdate(BaseModel):
    posicao: Optional[int] = None
    pontos: Optional[int] = None

class TabelaResponse(TabelaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# =======================
# PATROCINADORES
# =======================
class PatrocinadorBase(BaseModel):
    nome: str
    logo: Optional[str] = None

class PatrocinadorCreate(PatrocinadorBase):
    pass

class PatrocinadorUpdate(BaseModel):
    nome: Optional[str] = None
    logo: Optional[str] = None

class PatrocinadorResponse(PatrocinadorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

