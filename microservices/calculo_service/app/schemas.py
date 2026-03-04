"""Schemas Pydantic do serviço de cálculo"""

from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from typing import Optional


class CalculoInput(BaseModel):
    """Schema de entrada para cálculo"""

    valor_produtos: float = Field(..., ge=0, description="Valor total dos produtos")
    quantidade: int = Field(default=0, ge=0, description="Quantidade total de itens")
    peso_kg: float = Field(default=0, ge=0, description="Peso total em kg")
    distancia_km: float = Field(default=0, ge=0, description="Distância em km")
    tipo_desconto: str = Field(
        default="sem_desconto", description="Tipo de desconto a aplicar"
    )
    tipo_frete: str = Field(default="fixo_50", description="Tipo de frete a aplicar")


class ResultadoCalculo(BaseModel):
    """Schema de resultado do cálculo"""

    model_config = ConfigDict(from_attributes=True)

    valor_produtos: Decimal = Field(..., description="Valor total dos produtos")
    desconto: Decimal = Field(..., description="Valor do desconto aplicado")
    frete: Decimal = Field(..., description="Valor do frete")
    valor_final: Decimal = Field(..., description="Valor final do pedido")
    percentual_desconto: float = Field(
        ..., description="Percentual de desconto aplicado"
    )
    estrategia_desconto: str = Field(
        ..., description="Estratégia de desconto utilizada"
    )
    estrategia_frete: str = Field(..., description="Estratégia de frete utilizada")


class EstrategiaInfo(BaseModel):
    """Schema de informações da estratégia"""

    tipo: str
    nome: str
    descricao: str


class EstrategiasListResponse(BaseModel):
    """Schema de lista de estratégias"""

    desconto: list[EstrategiaInfo]
    frete: list[EstrategiaInfo]


class SimulacaoInput(BaseModel):
    """Schema para simulação com múltiplas estratégias"""

    valor_produtos: float = Field(..., ge=0)
    quantidade: int = Field(default=0, ge=0)
    peso_kg: float = Field(default=0, ge=0)
    distancia_km: float = Field(default=0, ge=0)
    estrategias_desconto: list[str] = Field(default=["sem_desconto"])
    estrategias_frete: list[str] = Field(default=["fixo_50"])


class SimulacaoResultado(BaseModel):
    """Schema de resultado de simulação"""

    tipo_desconto: str
    tipo_frete: str
    valor_produtos: float
    desconto: float
    frete: float
    valor_final: float
    percentual_desconto: float


class SimulacaoResponse(BaseModel):
    """Schema de resposta de simulação"""

    resultados: list[SimulacaoResultado]
    melhor_opcao: SimulacaoResultado
