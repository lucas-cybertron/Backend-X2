from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from models.models import Partida, Tabela, Time
from schemas.schemas import (
    PartidaCreate,
    PartidaUpdate,
    PartidaResponse,
    TabelaResponse,
)


# ===========================================================
# 🔹 SERVIÇOS DE PARTIDAS COM HISTÓRICO
# ===========================================================


def create_partida(partida_data: PartidaCreate, db: Session) -> PartidaResponse:
    """
    Cria uma nova partida e armazena no histórico
    
    Args:
        partida_data: Dados da partida
        db: Sessão do banco de dados
        
    Returns:
        PartidaResponse com dados da partida criada
        
    Raises:
        HTTPException: Se times não existem ou são iguais
    """
    # Valida se os times existem
    time_mandante = db.query(Time).filter(Time.id == partida_data.time_mandante_id).first()
    time_visitante = db.query(Time).filter(Time.id == partida_data.time_visitante_id).first()

    if not time_mandante or not time_visitante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Um ou ambos os times não foram encontrados",
        )

    if partida_data.time_mandante_id == partida_data.time_visitante_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time mandante e visitante não podem ser iguais",
        )

    new_partida = Partida(
        data_hora=partida_data.data_hora,
        local=partida_data.local,
        placar_mandante=partida_data.placar_mandante,
        placar_visitante=partida_data.placar_visitante,
        time_mandante_id=partida_data.time_mandante_id,
        time_visitante_id=partida_data.time_visitante_id,
    )

    db.add(new_partida)
    db.commit()
    db.refresh(new_partida)

    # Atualiza a tabela de classificação
    atualizar_tabela(db)

    return PartidaResponse.from_orm(new_partida)


def get_all_partidas(db: Session, skip: int = 0, limit: int = 100) -> list[PartidaResponse]:
    """
    Lista todas as partidas (histórico)
    
    Args:
        db: Sessão do banco de dados
        skip: Número de registros a pular (paginação)
        limit: Número máximo de registros
        
    Returns:
        Lista de PartidaResponse
    """
    partidas = db.query(Partida).order_by(Partida.data_hora.desc()).offset(skip).limit(limit).all()
    return [PartidaResponse.from_orm(p) for p in partidas]


def get_partida_by_id(partida_id: int, db: Session) -> PartidaResponse:
    """
    Busca uma partida pelo ID
    
    Args:
        partida_id: ID da partida
        db: Sessão do banco de dados
        
    Returns:
        PartidaResponse
        
    Raises:
        HTTPException: Se partida não encontrada
    """
    partida = db.query(Partida).filter(Partida.id == partida_id).first()

    if not partida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida não encontrada",
        )

    return PartidaResponse.from_orm(partida)


def update_partida(partida_id: int, partida_data: PartidaUpdate, db: Session) -> PartidaResponse:
    """
    Atualiza placar de uma partida e regenera tabela
    
    Args:
        partida_id: ID da partida
        partida_data: Novos dados (placar)
        db: Sessão do banco de dados
        
    Returns:
        PartidaResponse atualizada
        
    Raises:
        HTTPException: Se partida não encontrada
    """
    partida = db.query(Partida).filter(Partida.id == partida_id).first()

    if not partida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida não encontrada",
        )

    if partida_data.placar_mandante is not None:
        partida.placar_mandante = partida_data.placar_mandante
    if partida_data.placar_visitante is not None:
        partida.placar_visitante = partida_data.placar_visitante

    partida.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(partida)

    # Regenera a tabela após atualização
    atualizar_tabela(db)

    return PartidaResponse.from_orm(partida)


def delete_partida(partida_id: int, db: Session) -> dict:
    """
    Deleta uma partida do histórico
    
    Args:
        partida_id: ID da partida
        db: Sessão do banco de dados
        
    Returns:
        Mensagem de sucesso
    """
    partida = db.query(Partida).filter(Partida.id == partida_id).first()

    if not partida:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida não encontrada",
        )

    db.delete(partida)
    db.commit()

    # Regenera a tabela após deleção
    atualizar_tabela(db)

    return {"message": "Partida deletada com sucesso"}


# ===========================================================
# 🔹 SERVIÇOS DE TABELA DE CLASSIFICAÇÃO
# ===========================================================


def atualizar_tabela(db: Session) -> None:
    """
    Atualiza a tabela de classificação baseada no histórico de partidas
    Calcula automaticamente: pontos, vitórias, empates, derrotas, gols
    
    Args:
        db: Sessão do banco de dados
    """
    # Limpa a tabela antiga
    db.query(Tabela).delete()
    db.commit()

    # Busca todos os times
    times = db.query(Time).all()

    # Dicionário para armazenar dados de cada time
    dados_times = {}

    for time in times:
        dados_times[time.id] = {
            "time_id": time.id,
            "posicao": 0,
            "pontos": 0,
            "jogos": 0,
            "vitorias": 0,
            "empates": 0,
            "derrotas": 0,
            "gols_pro": 0,
            "gols_contra": 0,
        }

    # Processa todas as partidas
    partidas = db.query(Partida).all()

    for partida in partidas:
        time_mandante_id = partida.time_mandante_id
        time_visitante_id = partida.time_visitante_id
        placar_mandante = partida.placar_mandante
        placar_visitante = partida.placar_visitante

        # Atualiza time mandante
        dados_times[time_mandante_id]["jogos"] += 1
        dados_times[time_mandante_id]["gols_pro"] += placar_mandante
        dados_times[time_mandante_id]["gols_contra"] += placar_visitante

        # Atualiza time visitante
        dados_times[time_visitante_id]["jogos"] += 1
        dados_times[time_visitante_id]["gols_pro"] += placar_visitante
        dados_times[time_visitante_id]["gols_contra"] += placar_mandante

        # Calcula pontos e resultados
        if placar_mandante > placar_visitante:
            # Vitória do mandante
            dados_times[time_mandante_id]["vitorias"] += 1
            dados_times[time_mandante_id]["pontos"] += 3
            dados_times[time_visitante_id]["derrotas"] += 1
        elif placar_visitante > placar_mandante:
            # Vitória do visitante
            dados_times[time_visitante_id]["vitorias"] += 1
            dados_times[time_visitante_id]["pontos"] += 3
            dados_times[time_mandante_id]["derrotas"] += 1
        else:
            # Empate
            dados_times[time_mandante_id]["empates"] += 1
            dados_times[time_mandante_id]["pontos"] += 1
            dados_times[time_visitante_id]["empates"] += 1
            dados_times[time_visitante_id]["pontos"] += 1

    # Ordena por pontos (decrescente) e saldo de gols
    lista_times = list(dados_times.values())
    lista_times.sort(
        key=lambda x: (x["pontos"], x["gols_pro"] - x["gols_contra"]),
        reverse=True,
    )

    # Atribui posições e insere na tabela
    for posicao, dados in enumerate(lista_times, 1):
        dados["posicao"] = posicao
        dados["saldo_gols"] = dados["gols_pro"] - dados["gols_contra"]

        nova_linha_tabela = Tabela(
            posicao=dados["posicao"],
            pontos=dados["pontos"],
            jogos=dados["jogos"],
            vitorias=dados["vitorias"],
            empates=dados["empates"],
            derrotas=dados["derrotas"],
            gols_pro=dados["gols_pro"],
            gols_contra=dados["gols_contra"],
            saldo_gols=dados["saldo_gols"],
            time_id=dados["time_id"],
        )

        db.add(nova_linha_tabela)

    db.commit()


def get_tabela(db: Session) -> list[TabelaResponse]:
    """
    Retorna a tabela de classificação ordenada por posição com nomes dos times
    
    Args:
        db: Sessão do banco de dados
        
    Returns:
        Lista de TabelaResponse
    """
    tabela = db.query(Tabela).order_by(Tabela.posicao).all()

    if not tabela:
        # Se a tabela estiver vazia, atualiza
        atualizar_tabela(db)
        tabela = db.query(Tabela).order_by(Tabela.posicao).all()

    result = []
    for t in tabela:
        time = db.query(Time).filter(Time.id == t.time_id).first()
        time_nome = time.nome if time else None
        
        response = TabelaResponse.from_orm(t)
        response.time_nome = time_nome
        result.append(response)
    
    return result


def get_posicao_time(time_id: int, db: Session) -> TabelaResponse:
    """
    Busca a posição de um time na tabela com seu nome
    
    Args:
        time_id: ID do time
        db: Sessão do banco de dados
        
    Returns:
        TabelaResponse com dados do time
        
    Raises:
        HTTPException: Se time não está na tabela
    """
    posicao = db.query(Tabela).filter(Tabela.time_id == time_id).first()

    if not posicao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado na tabela",
        )

    time = db.query(Time).filter(Time.id == time_id).first()
    time_nome = time.nome if time else None
    
    response = TabelaResponse.from_orm(posicao)
    response.time_nome = time_nome
    
    return response
