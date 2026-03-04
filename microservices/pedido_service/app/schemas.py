"""Schemas Pydantic do serviço de pedidos"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum


class StatusPedido(str, Enum):
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    EM_SEPARACAO = "em_separacao"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class TipoDesconto(str, Enum):
    PERCENTUAL_10 = "percentual_10"
    PERCENTUAL_15 = "percentual_15"
    PERCENTUAL_20 = "percentual_20"
    PERCENTUAL_30 = "percentual_30"
    FIXO_50 = "fixo_50"
    FIXO_100 = "fixo_100"
    PROGRESSIVO = "progressivo"
    SEM_DESCONTO = "sem_desconto"


class TipoFrete(str, Enum):
    POR_PESO = "por_peso"
    POR_DISTANCIA = "por_distancia"
    FIXO_30 = "fixo_30"
    FIXO_50 = "fixo_50"
    GRATIS = "gratis"


# Item do Pedido
class ItemPedidoBase(BaseModel):
    """Schema base para item do pedido"""

    produto_id: int = Field(..., gt=0, description="ID do produto")
    quantidade: int = Field(..., gt=0, description="Quantidade")


class ItemPedidoCreate(ItemPedidoBase):
    """Schema para criar item do pedido"""

    pass


class ItemPedidoResponse(BaseModel):
    """Schema de resposta do item do pedido"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    nome_produto: str
    preco_unitario: Decimal
    quantidade: int
    peso_unitario: float
    subtotal: Decimal


# Pedido
class PedidoBase(BaseModel):
    """Schema base de pedido"""

    tipo_desconto: TipoDesconto = Field(default=TipoDesconto.SEM_DESCONTO)
    tipo_frete: TipoFrete = Field(default=TipoFrete.FIXO_50)
    distancia_km: float = Field(
        default=0, ge=0, description="Distância para entrega em km"
    )
    endereco_entrega: Optional[str] = Field(None, max_length=500)
    observacoes: Optional[str] = Field(None, max_length=1000)


class PedidoCreate(PedidoBase):
    """Schema para criar pedido"""

    itens: list[ItemPedidoCreate] = Field(
        ..., min_length=1, description="Itens do pedido"
    )


class PedidoUpdate(BaseModel):
    """Schema para atualizar pedido"""

    status: Optional[StatusPedido] = None
    tipo_desconto: Optional[TipoDesconto] = None
    tipo_frete: Optional[TipoFrete] = None
    distancia_km: Optional[float] = Field(None, ge=0)
    endereco_entrega: Optional[str] = Field(None, max_length=500)
    observacoes: Optional[str] = Field(None, max_length=1000)


class PedidoResponse(PedidoBase):
    """Schema de resposta de pedido"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    usuario_id: Optional[int] = None
    status: str
    valor_produtos: Decimal
    valor_desconto: Decimal
    valor_frete: Decimal
    valor_total: Decimal
    peso_total: float
    itens: list[ItemPedidoResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PedidoResumoResponse(BaseModel):
    """Schema de resumo do pedido (sem itens)"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    status: str
    valor_total: Decimal
    created_at: Optional[datetime] = None


class PedidoListResponse(BaseModel):
    """Schema de lista de pedidos"""

    items: list[PedidoResumoResponse]
    total: int
    page: int
    per_page: int
    pages: int


class RecalcularPedidoRequest(BaseModel):
    """Schema para recalcular pedido"""

    tipo_desconto: Optional[TipoDesconto] = None
    tipo_frete: Optional[TipoFrete] = None
    distancia_km: Optional[float] = None


class MessageResponse(BaseModel):
    """Schema para mensagens de resposta"""

    message: str
    success: bool = True
