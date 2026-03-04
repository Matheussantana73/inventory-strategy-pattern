"""Rotas da API de autenticação"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from shared.database import get_db
from shared.redis_client import CacheService, EventBus

from .models import Usuario, TokenRevogado
from .schemas import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
    AlterarSenha,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    MessageResponse,
    ValidateTokenResponse,
)
from .auth import (
    hash_senha,
    verificar_senha,
    criar_access_token,
    criar_refresh_token,
    decodificar_token,
    extrair_jti,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])

# Serviços
cache = CacheService(prefix="auth")
event_bus = EventBus()
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Usuario:
    """Dependency para obter usuário atual do token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token não fornecido"
        )

    token = credentials.credentials
    payload = decodificar_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Tipo de token inválido"
        )

    # Verificar se token foi revogado
    jti = payload.get("jti")
    if jti:
        revogado = db.query(TokenRevogado).filter(TokenRevogado.jti == jti).first()
        if revogado:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token foi revogado"
            )

    user_id = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )

    return usuario


def get_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Dependency para verificar se é admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Permissão de administrador necessária.",
        )
    return current_user


@router.post(
    "/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
def registrar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário"""
    # Verificar se email já existe
    existente = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado"
        )

    # Criar usuário
    usuario = Usuario(
        email=dados.email, nome=dados.nome, senha_hash=hash_senha(dados.senha)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Publicar evento
    event_bus.publish("usuario.criado", {"id": usuario.id, "email": usuario.email})

    return usuario


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    """Realiza login e retorna tokens"""
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos"
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inativo"
        )

    # Atualizar último login
    usuario.last_login = datetime.utcnow()
    db.commit()

    # Criar tokens
    token_data = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "is_admin": usuario.is_admin,
    }

    access_token = criar_access_token(token_data)
    refresh_token = criar_refresh_token(token_data)

    # Publicar evento
    event_bus.publish("usuario.login", {"id": usuario.id, "email": usuario.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(dados: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Renova access token usando refresh token"""
    payload = decodificar_token(dados.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não é um refresh token",
        )

    # Verificar se foi revogado
    jti = payload.get("jti")
    if jti:
        revogado = db.query(TokenRevogado).filter(TokenRevogado.jti == jti).first()
        if revogado:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token foi revogado",
            )

    user_id = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )

    # Criar novos tokens
    token_data = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "is_admin": usuario.is_admin,
    }

    new_access_token = criar_access_token(token_data)
    new_refresh_token = criar_refresh_token(token_data)

    # Revogar refresh token antigo
    expira_em = datetime.fromtimestamp(payload.get("exp", 0))
    token_revogado = TokenRevogado(jti=jti, expira_em=expira_em)
    db.add(token_revogado)
    db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Realiza logout (revoga token)"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token não fornecido"
        )

    token = credentials.credentials
    payload = decodificar_token(token)

    if payload:
        jti = payload.get("jti")
        exp = payload.get("exp", 0)

        if jti:
            # Revogar token
            expira_em = datetime.fromtimestamp(exp)
            token_revogado = TokenRevogado(jti=jti, expira_em=expira_em)
            db.add(token_revogado)
            db.commit()

    return MessageResponse(message="Logout realizado com sucesso")


@router.get("/me", response_model=UsuarioResponse)
def obter_usuario_atual(current_user: Usuario = Depends(get_current_user)):
    """Retorna dados do usuário logado"""
    return current_user


@router.put("/me", response_model=UsuarioResponse)
def atualizar_usuario_atual(
    dados: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualiza dados do usuário logado"""
    # Apenas nome pode ser alterado pelo próprio usuário
    if dados.nome:
        current_user.nome = dados.nome

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/me/alterar-senha", response_model=MessageResponse)
def alterar_senha(
    dados: AlterarSenha,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Altera senha do usuário logado"""
    # Verificar senha atual
    if not verificar_senha(dados.senha_atual, current_user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta"
        )

    # Atualizar senha
    current_user.senha_hash = hash_senha(dados.nova_senha)
    db.commit()

    return MessageResponse(message="Senha alterada com sucesso")


@router.post("/validate", response_model=ValidateTokenResponse)
def validar_token(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    """Valida token (usado por outros serviços)"""
    if not authorization or not authorization.startswith("Bearer "):
        return ValidateTokenResponse(valid=False)

    token = authorization.replace("Bearer ", "")
    payload = decodificar_token(token)

    if not payload or payload.get("type") != "access":
        return ValidateTokenResponse(valid=False)

    # Verificar se foi revogado
    jti = payload.get("jti")
    if jti:
        revogado = db.query(TokenRevogado).filter(TokenRevogado.jti == jti).first()
        if revogado:
            return ValidateTokenResponse(valid=False)

    return ValidateTokenResponse(
        valid=True,
        user_id=int(payload.get("sub", 0)),
        email=payload.get("email"),
        is_admin=payload.get("is_admin", False),
    )


# Rotas administrativas
@router.get("/users", response_model=list[UsuarioResponse])
def listar_usuarios(
    admin: Usuario = Depends(get_admin_user), db: Session = Depends(get_db)
):
    """Lista todos os usuários (admin)"""
    return db.query(Usuario).all()


@router.put("/users/{user_id}", response_model=UsuarioResponse)
def atualizar_usuario(
    user_id: int,
    dados: UsuarioUpdate,
    admin: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Atualiza um usuário (admin)"""
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    # Atualizar campos
    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(usuario, field, value)

    db.commit()
    db.refresh(usuario)

    return usuario
