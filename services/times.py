from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.models import Time, Jogadores, Partida, Tabela, Patrocinadores
from schemas.schemas import (
    TimeCreate,
    TimeUpdate,
    TimeResponse,
    JogadorCreate,
    JogadorUpdate,
    JogadorResponse,
)


# ===========================================================
# 🔹 SERVIÇOS DE TIMES
# ===========================================================


def create_time(time_data: TimeCreate, db: Session) -> TimeResponse:
    """
    Cria um novo time
    
    Args:
        time_data: Dados do time (nome, escudo)
        db: Sessão do banco de dados
        
    Returns:
        TimeResponse com dados do time criado
        
    Raises:
        HTTPException: Se o nome do time já existe
    """
    existing_time = db.query(Time).filter(Time.nome == time_data.nome).first()
    if existing_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time com este nome já existe",
        )

    new_time = Time(
        nome=time_data.nome,
        escudo=time_data.escudo,
    )

    db.add(new_time)
    db.commit()
    db.refresh(new_time)

    return TimeResponse.from_orm(new_time)


def get_all_times(db: Session, skip: int = 0, limit: int = 100) -> list[TimeResponse]:
    """
    Lista todos os times
    
    Args:
        db: Sessão do banco de dados
        skip: Número de registros a pular (paginação)
        limit: Número máximo de registros a retornar
        
    Returns:
        Lista de TimeResponse
    """
    times = db.query(Time).offset(skip).limit(limit).all()
    return [TimeResponse.from_orm(time) for time in times]


def get_time_by_id(time_id: int, db: Session) -> TimeResponse:
    """
    Busca um time pelo ID
    
    Args:
        time_id: ID do time
        db: Sessão do banco de dados
        
    Returns:
        TimeResponse com dados do time
        
    Raises:
        HTTPException: Se time não encontrado
    """
    time = db.query(Time).filter(Time.id == time_id).first()

    if not time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado",
        )

    return TimeResponse.from_orm(time)


def update_time(time_id: int, time_data: TimeUpdate, db: Session) -> TimeResponse:
    """
    Atualiza dados de um time
    
    Args:
        time_id: ID do time
        time_data: Novos dados do time
        db: Sessão do banco de dados
        
    Returns:
        TimeResponse com dados atualizados
        
    Raises:
        HTTPException: Se time não encontrado
    """
    time = db.query(Time).filter(Time.id == time_id).first()

    if not time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado",
        )

    if time_data.nome:
        time.nome = time_data.nome
    if time_data.escudo:
        time.escudo = time_data.escudo

    db.commit()
    db.refresh(time)

    return TimeResponse.from_orm(time)


def delete_time(time_id: int, db: Session) -> dict:
    """
    Deleta um time
    
    Args:
        time_id: ID do time
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se time não encontrado
    """
    time = db.query(Time).filter(Time.id == time_id).first()

    if not time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado",
        )

    db.delete(time)
    db.commit()

    return {"message": "Time deletado com sucesso"}


# ===========================================================
# 🔹 SERVIÇOS DE JOGADORES
# ===========================================================


def create_jogador(jogador_data: JogadorCreate, db: Session) -> JogadorResponse:
    """
    Cria um novo jogador
    
    Args:
        jogador_data: Dados do jogador
        db: Sessão do banco de dados
        
    Returns:
        JogadorResponse com dados do jogador
        
    Raises:
        HTTPException: Se time não existe
    """
    # Valida se o time existe
    time = db.query(Time).filter(Time.id == jogador_data.time_id).first()
    if not time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado",
        )

    new_jogador = Jogadores(
        nome=jogador_data.nome,
        data_nascimento=jogador_data.data_nascimento,
        time_id=jogador_data.time_id,
    )

    db.add(new_jogador)
    db.commit()
    db.refresh(new_jogador)

    return JogadorResponse.from_orm(new_jogador)


def get_jogadores_by_time(time_id: int, db: Session) -> list[JogadorResponse]:
    """
    Lista todos os jogadores de um time
    
    Args:
        time_id: ID do time
        db: Sessão do banco de dados
        
    Returns:
        Lista de JogadorResponse
    """
    jogadores = db.query(Jogadores).filter(Jogadores.time_id == time_id).all()
    return [JogadorResponse.from_orm(j) for j in jogadores]


def update_jogador(jogador_id: int, jogador_data: JogadorUpdate, db: Session) -> JogadorResponse:
    """
    Atualiza dados de um jogador
    
    Args:
        jogador_id: ID do jogador
        jogador_data: Novos dados
        db: Sessão do banco de dados
        
    Returns:
        JogadorResponse atualizado
    """
    jogador = db.query(Jogadores).filter(Jogadores.id == jogador_id).first()

    if not jogador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador não encontrado",
        )

    if jogador_data.nome:
        jogador.nome = jogador_data.nome
    if jogador_data.data_nascimento:
        jogador.data_nascimento = jogador_data.data_nascimento

    db.commit()
    db.refresh(jogador)

    return JogadorResponse.from_orm(jogador)


def delete_jogador(jogador_id: int, db: Session) -> dict:
    """
    Deleta um jogador
    
    Args:
        jogador_id: ID do jogador
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
    """
    jogador = db.query(Jogadores).filter(Jogadores.id == jogador_id).first()

    if not jogador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jogador não encontrado",
        )

    db.delete(jogador)
    db.commit()

    return {"message": "Jogador deletado com sucesso"}
