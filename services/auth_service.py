# services/auth_service.py
from sqlalchemy.orm import Session
from models.user import User
from core.security import verify_password, create_access_token
from datetime import timedelta
from fastapi import HTTPException, status

# ===========================================================
# 🔹 Autentica o usuário e retorna um token JWT
# ===========================================================
def authenticate_user(db: Session, email: str, password: str):
    """Verifica se o usuário existe e se a senha está correta"""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta"
        )

    return user


def create_login_token(user: User):
    """Cria o token JWT a partir do usuário autenticado"""
    access_token_expires = timedelta(hours=1)
    token_data = {"sub": str(user.id), "type": user.type.value}
    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
