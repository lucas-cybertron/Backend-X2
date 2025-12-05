from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from datetime import timedelta

from core.database import get_db
from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from models.models import User
from schemas.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    ChangePasswordRequest,
)

# ===========================================================
# 🔹 Configuração do Router
# ===========================================================
router = APIRouter(
    prefix="/auth",
    tags=["autenticação"],
    responses={404: {"description": "Não encontrado"}},
)


# ===========================================================
# 🔹 DEPENDÊNCIAS
# ===========================================================


def get_token(authorization: str = Header(None)) -> str | None:
    """
    Extrai o token JWT do header Authorization com formato: Bearer <token>
    
    Exemplo:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]

    return None


def get_current_user_id(token: str = Depends(get_token)) -> int:
    """
    Autentica o token JWT e retorna o ID do usuário
    
    Fluxo:
    1. Extrai o token do header Authorization
    2. Decodifica e valida o token JWT
    3. Verifica se o token é válido e não expirou
    4. Retorna o ID do usuário dentro do token
    
    Raises:
        HTTPException 401: Se o token não for fornecido, inválido ou expirado
    """
    from core.security import decode_access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return int(user_id)


def get_current_admin(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    """
    Verifica se o usuário autenticado é um administrador
    
    Uso em endpoints protegidos:
        @router.delete("/admin/users/{user_id}")
        def delete_user(user_id: int, admin: User = Depends(get_current_admin)):
            # Só admins podem acessar
    
    Args:
        current_user_id: ID do usuário autenticado (via token JWT)
        db: Sessão do banco de dados
        
    Returns:
        User: Objeto do usuário admin
        
    Raises:
        HTTPException 403: Se o usuário não é admin
        HTTPException 404: Se o usuário não foi encontrado
    """
    user = db.query(User).filter(User.id == current_user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    if user.type.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas administradores podem acessar este recurso",
        )
    
    return user



# ===========================================================
# 🔹 ENDPOINTS DE AUTENTICAÇÃO
# ===========================================================


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra um novo usuário
    
    - **email**: Email único do usuário
    - **password**: Senha com mínimo 6 caracteres
    - **name**: Nome completo do usuário
    - **phone**: Número de telefone (opcional)
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


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login do usuário
    
    - **email**: Email registrado
    - **password**: Senha do usuário
    
    Retorna access_token, refresh_token e dados do usuário
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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token: str, db: Session = Depends(get_db)):
    """
    Renova o access token usando o refresh token
    
    - **token**: Refresh token válido
    
    Retorna novo access_token
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


@router.put("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Altera a senha do usuário autenticado
    
    - **current_password**: Senha atual
    - **new_password**: Nova senha (mínimo 6 caracteres)
    """
    user = db.query(User).filter(User.id == current_user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    if not verify_password(data.current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta",
        )

    user.password = get_password_hash(data.new_password)
    db.commit()

    return {"message": "Senha alterada com sucesso"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Endpoint protegido que retorna os dados do usuário autenticado
    
    Requer autenticação com Bearer Token:
        Authorization: Bearer <seu_access_token>
    
    Returns:
        UserResponse: Dados do usuário logado
        
    Raises:
        401: Token inválido ou expirado
        404: Usuário não encontrado
    """
    """
    Retorna os dados do usuário autenticado
    """
    user = db.query(User).filter(User.id == current_user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    return UserResponse.from_orm(user)
