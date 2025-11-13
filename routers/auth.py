# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_password_hash, decode_access_token as verify_token
from schemas.user import UserCreate, UserLogin, Token, UserResponse
from models.user import User
from services.auth_service import authenticate_user, create_login_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# ===========================================================
# 🔹 Cadastro de usuário
# ===========================================================
@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Cria um novo usuário no banco"""
    user_exists = db.query(User).filter(User.email == user_data.email).first()

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password=hashed_password,
        type=user_data.type
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ===========================================================
# 🔹 Login
# ===========================================================
@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Autentica usuário e retorna token JWT"""
    user = authenticate_user(db, user_data.email, user_data.password)
    return create_login_token(user)


# ===========================================================
# 🔹 Rota protegida (teste)
# ===========================================================
@router.get("/me", response_model=UserResponse)
def get_me(token_data=Depends(verify_token), db: Session = Depends(get_db)):
    """Retorna os dados do usuário autenticado"""
    user = db.query(User).filter(User.id == token_data.get("sub")).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return user
