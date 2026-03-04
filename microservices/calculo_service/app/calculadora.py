"""Calculadora de Pedidos"""

from decimal import Decimal
from typing import Union

from .strategies import EstrategiaDesconto, EstrategiaFrete
from .schemas import ResultadoCalculo


class CalculadoraPedido:
    """Contexto que utiliza as estratégias de desconto e frete"""

    def __init__(
        self, estrategia_desconto: EstrategiaDesconto, estrategia_frete: EstrategiaFrete
    ):
        """
        Inicializa a calculadora com estratégias específicas

        Args:
            estrategia_desconto: Estratégia de desconto a ser utilizada
            estrategia_frete: Estratégia de frete a ser utilizada
        """
        self._estrategia_desconto = estrategia_desconto
        self._estrategia_frete = estrategia_frete

    def set_estrategia_desconto(self, estrategia: EstrategiaDesconto) -> None:
        """Troca a estratégia de desconto dinamicamente"""
        self._estrategia_desconto = estrategia

    def set_estrategia_frete(self, estrategia: EstrategiaFrete) -> None:
        """Troca a estratégia de frete dinamicamente"""
        self._estrategia_frete = estrategia

    def calcular_total(
        self,
        valor_produtos: Union[float, Decimal],
        quantidade: int = 0,
        peso_kg: Union[float, Decimal] = 0,
        distancia_km: Union[float, Decimal] = 0,
    ) -> ResultadoCalculo:
        """
        Calcula o total do pedido com desconto e frete

        Args:
            valor_produtos: Valor total dos produtos
            quantidade: Quantidade total de itens
            peso_kg: Peso total em kg
            distancia_km: Distância em km

        Returns:
            ResultadoCalculo com breakdown dos valores
        """
        # Converter para Decimal para precisão
        valor_produtos_decimal = Decimal(str(valor_produtos))
        peso_kg_float = float(peso_kg)
        distancia_km_float = float(distancia_km)

        # Calcular desconto
        desconto = Decimal(
            str(
                self._estrategia_desconto.calcular_desconto(
                    float(valor_produtos_decimal),
                    quantidade=quantidade,
                    valor_produtos=float(valor_produtos_decimal),
                )
            )
        )

        # Calcular frete
        frete = Decimal(
            str(
                self._estrategia_frete.calcular_frete(
                    peso_kg=peso_kg_float,
                    distancia_km=distancia_km_float,
                    valor_produtos=float(valor_produtos_decimal),
                )
            )
        )

        # Calcular valor final
        valor_final = valor_produtos_decimal - desconto + frete

        # Calcular percentual de desconto
        if valor_produtos_decimal > 0:
            percentual_desconto = float((desconto / valor_produtos_decimal) * 100)
        else:
            percentual_desconto = 0.0

        return ResultadoCalculo(
            valor_produtos=valor_produtos_decimal,
            desconto=desconto,
            frete=frete,
            valor_final=valor_final,
            percentual_desconto=round(percentual_desconto, 2),
            estrategia_desconto=self._estrategia_desconto.nome,
            estrategia_frete=self._estrategia_frete.nome,
        )
