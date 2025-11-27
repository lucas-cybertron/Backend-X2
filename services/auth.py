from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from models.models import User
from schemas.schemas import UserRegister, UserLogin, TokenResponse, UserResponse


# ===========================================================
# 🔹 SERVIÇOS DE AUTENTICAÇÃO
# ===========================================================


def register_user(user_data: UserRegister, db: Session) -> TokenResponse:
    """
    Registra um novo usuário e retorna tokens JWT
    
    Args:
        user_data: Dados do usuário (email, password, name, phone)
        db: Sessão do banco de dados
        
    Returns:
        TokenResponse com access_token, refresh_token e dados do usuário
        
    Raises:
        HTTPException: Se o email já está registrado
    """
    # Verifica se o usuário já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado",
        )

    # Cria novo usuário
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password=hashed_password,
        name=user_data.name,
        phone=user_data.phone,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Gera tokens
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(new_user),
    }


def login_user(credentials: UserLogin, db: Session) -> TokenResponse:
    """
    Realiza o login do usuário e retorna tokens JWT
    
    Args:
        credentials: Email e senha do usuário
        db: Sessão do banco de dados
        
    Returns:
        TokenResponse com access_token, refresh_token e dados do usuário
        
    Raises:
        HTTPException: Se email ou senha estão incorretos
    """
    # Busca o usuário pelo email
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Gera tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user),
    }


def refresh_access_token(token: str, db: Session) -> TokenResponse:
    """
    Renova o access token usando um refresh token válido
    
    Args:
        token: Refresh token válido
        db: Sessão do banco de dados
        
    Returns:
        TokenResponse com novo access_token
        
    Raises:
        HTTPException: Se refresh token é inválido ou expirado
    """
    payload = decode_refresh_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    # Gera novo access token
    new_access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user),
    }


def change_password(current_user_id: int, current_password: str, new_password: str, db: Session) -> dict:
    """
    Altera a senha do usuário autenticado
    
    Args:
        current_user_id: ID do usuário autenticado
        current_password: Senha atual (para validação)
        new_password: Nova senha
        db: Sessão do banco de dados
        
    Returns:
        Dicionário com mensagem de sucesso
        
    Raises:
        HTTPException: Se usuário não encontrado ou senha atual incorreta
    """
    user = db.query(User).filter(User.id == current_user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    if not verify_password(current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta",
        )

    user.password = get_password_hash(new_password)
    db.commit()

    return {"message": "Senha alterada com sucesso"}


def get_user_by_id(user_id: int, db: Session) -> UserResponse:
    """
    Busca um usuário pelo ID
    
    Args:
        user_id: ID do usuário
        db: Sessão do banco de dados
        
    Returns:
        UserResponse com dados do usuário
        
    Raises:
        HTTPException: Se usuário não encontrado
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    return UserResponse.from_orm(user)
