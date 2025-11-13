# models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Enum
from core.database import Base
from datetime import datetime, timezone
import enum

# ===========================================================
# 🔹 Enum: define os tipos de usuário permitidos
# ===========================================================
class UserType(str, enum.Enum):
    SUPERADM = "superadm"
    ADM = "adm"
    CLIENTE = "cliente"

# ===========================================================
# 🔹 Modelo da tabela "users"
# ===========================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    type = Column(Enum(UserType), default=UserType.CLIENTE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
