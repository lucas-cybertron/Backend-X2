from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone
import enum
from sqlalchemy import Enum as PgEnum

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String , unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    type = Column(PgEnum(UserRole, name="user_role_enum"), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)  
    
class Jogadores(Base):
    __tablename__ = "jogadores"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    time_id = Column(Integer, ForeignKey("times.id"), nullable=False)  # <-- ID do time
    time = relationship("Time", back_populates="jogadores")  
    
class Time(Base):
    __tablename__ = "times"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    escudo = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    jogadores = relationship("Jogadores", back_populates="time")
    
class Partida(Base):
    __tablename__ = "partidas"
    
    id = Column(Integer, primary_key=True, index=True)
    data_hora = Column(DateTime, nullable=False)
    local = Column(String, nullable=False)
    placar_mandante = Column(Integer, default=0, nullable=False)
    placar_visitante = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    time_mandante_id = Column(Integer, ForeignKey("times.id"), nullable=False)
    time_visitante_id = Column(Integer, ForeignKey("times.id"), nullable=False)
    
    time_mandante = relationship("Time", foreign_keys=[time_mandante_id])
    time_visitante = relationship("Time", foreign_keys=[time_visitante_id])
    
class Tabela(Base):
    __tablename__ = "tabela"
    
    id = Column(Integer, primary_key=True, index=True)
    posicao = Column(Integer, nullable=False)
    pontos = Column(Integer, nullable=False)
    jogos = Column(Integer, nullable=False)
    vitorias = Column(Integer, nullable=False)
    empates = Column(Integer, nullable=False)
    derrotas = Column(Integer, nullable=False)
    gols_pro = Column(Integer, nullable=False)
    gols_contra = Column(Integer, nullable=False)
    saldo_gols = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    time_id = Column(Integer, ForeignKey("times.id"), nullable=False)
    time = relationship("Time")
    
class TournamentBracket(Base):
    __tablename__ = "tournament_brackets"

    id = Column(Integer, primary_key=True, index=True)
    tournament_name = Column(String, nullable=True)
    round = Column(Integer, nullable=False, default=1)
    match_number = Column(Integer, nullable=False, default=1)

    team_a_id = Column(Integer, ForeignKey("times.id"), nullable=True)
    team_b_id = Column(Integer, ForeignKey("times.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("times.id"), nullable=True)

    # Denormalized name fields to make it easy to inspect persisted brackets
    team_a_name = Column(String, nullable=True)
    team_b_name = Column(String, nullable=True)
    winner_name = Column(String, nullable=True)
    # Optional scores for each match
    team_a_score = Column(Integer, nullable=True)
    team_b_score = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    team_a = relationship("Time", foreign_keys=[team_a_id])
    team_b = relationship("Time", foreign_keys=[team_b_id])
    winner = relationship("Time", foreign_keys=[winner_id])

class Patrocinadores(Base):
    __tablename__ = "patrocinadores"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    