"""Módulo de estratégias"""

from .desconto import (
    EstrategiaDesconto,
    DescontoPercentual,
    DescontoFixo,
    DescontoProgressivo,
    DescontoPorValor,
    SemDesconto,
    ESTRATEGIAS_DESCONTO,
    obter_estrategia_desconto,
    listar_estrategias_desconto,
)
from .frete import (
    EstrategiaFrete,
    FretePorPeso,
    FretePorDistancia,
    FretePorPesoDistancia,
    FreteFixo,
    FreteGratis,
    FreteCondicional,
    ESTRATEGIAS_FRETE,
    obter_estrategia_frete,
    listar_estrategias_frete,
)

__all__ = [
    # Desconto
    "EstrategiaDesconto",
    "DescontoPercentual",
    "DescontoFixo",
    "DescontoProgressivo",
    "DescontoPorValor",
    "SemDesconto",
    "ESTRATEGIAS_DESCONTO",
    "obter_estrategia_desconto",
    "listar_estrategias_desconto",
    # Frete
    "EstrategiaFrete",
    "FretePorPeso",
    "FretePorDistancia",
    "FretePorPesoDistancia",
    "FreteFixo",
    "FreteGratis",
    "FreteCondicional",
    "ESTRATEGIAS_FRETE",
    "obter_estrategia_frete",
    "listar_estrategias_frete",
]
