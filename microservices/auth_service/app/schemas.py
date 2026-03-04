"""Schemas Pydantic do serviço de autenticação"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    """Schema base de usuário"""

    email: EmailStr = Field(..., description="Email do usuário")
    nome: str = Field(..., min_length=2, max_length=200, description="Nome completo")


class UsuarioCreate(UsuarioBase):
    """Schema para criação de usuário"""

    senha: str = Field(
        ..., min_length=6, max_length=100, description="Senha do usuário"
    )


class UsuarioResponse(UsuarioBase):
    """Schema de resposta de usuário"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool
    is_admin: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UsuarioUpdate(BaseModel):
    """Schema para atualização de usuário"""

    nome: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    ativo: Optional[bool] = None
    is_admin: Optional[bool] = None


class AlterarSenha(BaseModel):
    """Schema para alterar senha"""

    senha_atual: str = Field(..., min_length=1)
    nova_senha: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    """Schema para login"""

    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    """Schema de resposta de token"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Tempo de expiração em segundos")


class RefreshTokenRequest(BaseModel):
    """Schema para refresh token"""

    refresh_token: str


class MessageResponse(BaseModel):
    """Schema para mensagens"""

    message: str
    success: bool = True


class ValidateTokenResponse(BaseModel):
    """Schema para validação de token"""

    valid: bool
    user_id: Optional[int] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None
