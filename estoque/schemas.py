"""Schemas Pydantic para validação e serialização de dados"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ResultadoCalculoPedido(BaseModel):
    """Schema para resultado do cálculo de pedido"""
    
    model_config = ConfigDict(from_attributes=True)
    
    valor_produtos: Decimal = Field(..., description="Valor total dos produtos", ge=0)
    desconto: Decimal = Field(..., description="Valor do desconto aplicado", ge=0)
    frete: Decimal = Field(..., description="Valor do frete", ge=0)
    valor_final: Decimal = Field(..., description="Valor final do pedido", ge=0)
    
    @property
    def percentual_desconto(self) -> float:
        """Calcula o percentual de desconto aplicado"""
        if self.valor_produtos > 0:
            return float((self.desconto / self.valor_produtos) * 100)
        return 0.0


class ItemPedidoInput(BaseModel):
    """Schema para entrada de item de pedido"""
    
    model_config = ConfigDict(from_attributes=True)
    
    produto_id: int = Field(..., description="ID do produto", gt=0)
    quantidade: int = Field(..., description="Quantidade do produto", gt=0)
    preco_unitario: Optional[Decimal] = Field(None, description="Preço unitário do produto", ge=0)


class PedidoInput(BaseModel):
    """Schema para criação de pedido"""
    
    model_config = ConfigDict(from_attributes=True)
    
    numero: str = Field(..., description="Número do pedido", min_length=1, max_length=50)
    tipo_desconto: str = Field(default="sem_desconto", description="Tipo de desconto a aplicar")
    tipo_frete: str = Field(default="frete_fixo", description="Tipo de frete a aplicar")
    itens: list[ItemPedidoInput] = Field(..., description="Itens do pedido", min_length=1)


class CalculoInput(BaseModel):
    """Schema para entrada de cálculo de pedido"""
    
    model_config = ConfigDict(from_attributes=True)
    
    valor_produtos: Decimal = Field(..., description="Valor total dos produtos", ge=0)
    quantidade: int = Field(default=0, description="Quantidade total de itens", ge=0)
    peso_kg: Decimal = Field(default=0, description="Peso total em kg", ge=0)
    distancia_km: Decimal = Field(default=0, description="Distância em km", ge=0)


class EstrategiaDescontoConfig(BaseModel):
    """Schema para configuração de estratégia de desconto"""
    
    model_config = ConfigDict(from_attributes=True)
    
    tipo: str = Field(..., description="Tipo de desconto")
    percentual: Optional[float] = Field(None, description="Percentual de desconto", ge=0, le=100)
    valor_fixo: Optional[Decimal] = Field(None, description="Valor fixo de desconto", ge=0)
    faixas: Optional[dict[int, float]] = Field(None, description="Faixas progressivas de desconto")


class EstrategiaFreteConfig(BaseModel):
    """Schema para configuração de estratégia de frete"""
    
    model_config = ConfigDict(from_attributes=True)
    
    tipo: str = Field(..., description="Tipo de frete")
    valor_por_kg: Optional[Decimal] = Field(None, description="Valor por kg", ge=0)
    valor_por_km: Optional[Decimal] = Field(None, description="Valor por km", ge=0)
    valor_fixo: Optional[Decimal] = Field(None, description="Valor fixo de frete", ge=0)
