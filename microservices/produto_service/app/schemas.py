"""Schemas Pydantic do serviço de produtos"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ProdutoBase(BaseModel):
    """Schema base de produto"""

    nome: str = Field(..., min_length=1, max_length=200, description="Nome do produto")
    descricao: Optional[str] = Field(
        None, max_length=500, description="Descrição do produto"
    )
    preco: Decimal = Field(..., gt=0, description="Preço do produto")
    peso: float = Field(default=0, ge=0, description="Peso em kg")
    quantidade_estoque: int = Field(
        default=0, ge=0, description="Quantidade em estoque"
    )
    categoria: Optional[str] = Field(
        None, max_length=100, description="Categoria do produto"
    )
    sku: Optional[str] = Field(None, max_length=50, description="SKU do produto")


class ProdutoCreate(ProdutoBase):
    """Schema para criação de produto"""

    pass


class ProdutoUpdate(BaseModel):
    """Schema para atualização de produto"""

    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=500)
    preco: Optional[Decimal] = Field(None, gt=0)
    peso: Optional[float] = Field(None, ge=0)
    quantidade_estoque: Optional[int] = Field(None, ge=0)
    categoria: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=50)
    ativo: Optional[int] = Field(None, ge=0, le=1)


class ProdutoResponse(ProdutoBase):
    """Schema de resposta de produto"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EstoqueUpdate(BaseModel):
    """Schema para atualização de estoque"""

    quantidade: int = Field(
        ..., description="Quantidade a adicionar (positivo) ou remover (negativo)"
    )
    operacao: str = Field(
        default="set", description="Operação: 'set', 'add', 'subtract'"
    )


class ProdutoListResponse(BaseModel):
    """Schema de resposta de lista de produtos"""

    items: list[ProdutoResponse]
    total: int
    page: int
    per_page: int
    pages: int


class MessageResponse(BaseModel):
    """Schema para mensagens de resposta"""

    message: str
    success: bool = True
