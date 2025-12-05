#!/usr/bin/env python3
"""
Script para criar um usuário administrador no banco de dados
"""
from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from core.security import get_password_hash
from models.models import User, UserRole

def create_admin_user(email: str, password: str, name: str, phone: str = None) -> User:
    """Cria um novo usuário administrador"""
    
    db = SessionLocal()
    
    try:
        # Verifica se o usuário já existe
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ Erro: Usuário com email '{email}' já existe!")
            return None
        
        # Cria o novo admin
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            password=hashed_password,
            name=name,
            phone=phone,
            type=UserRole.ADMIN
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Admin criado com sucesso!")
        print(f"   Email: {admin_user.email}")
        print(f"   Nome: {admin_user.name}")
        print(f"   Tipo: {admin_user.type.value}")
        print(f"   ID: {admin_user.id}")
        
        return admin_user
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar admin: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 Criador de Usuário Administrador")
    print("=" * 60)
    
    email = input("📧 Email do admin: ").strip()
    password = input("🔑 Senha (mín. 6 caracteres): ").strip()
    name = input("👤 Nome completo: ").strip()
    phone = input("📱 Telefone (opcional, pressione Enter para pular): ").strip() or None
    
    # Validações
    if not email or "@" not in email:
        print("❌ Email inválido!")
        exit(1)
    
    if len(password) < 6:
        print("❌ Senha deve ter pelo menos 6 caracteres!")
        exit(1)
    
    if not name:
        print("❌ Nome é obrigatório!")
        exit(1)
    
    # Cria o admin
    admin = create_admin_user(email, password, name, phone)
    
    if admin:
        print("\n" + "=" * 60)
        print("✅ Agora você pode fazer login com:")
        print(f"   Email: {email}")
        print(f"   Senha: {password}")
        print("=" * 60)
