"""Calculadora de pedidos usando padrão Strategy"""
from decimal import Decimal
from typing import Union

from estoque.strategies.desconto import EstrategiaDesconto
from estoque.strategies.frete import EstrategiaFrete
from estoque.schemas import ResultadoCalculoPedido, CalculoInput


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
        """
        Troca a estratégia de desconto dinamicamente

        Args:
            estrategia: Nova estratégia de desconto
        """
        self._estrategia_desconto = estrategia

    def set_estrategia_frete(self, estrategia: EstrategiaFrete) -> None:
        """
        Troca a estratégia de frete dinamicamente

        Args:
            estrategia: Nova estratégia de frete
        """
        self._estrategia_frete = estrategia

    def calcular_total(
        self,
        valor_produtos: Union[float, Decimal],
        quantidade: int = 0,
        peso_kg: Union[float, Decimal] = 0,
        distancia_km: Union[float, Decimal] = 0,
    ) -> ResultadoCalculoPedido:
        """
        Calcula o total do pedido com desconto e frete

        Args:
            valor_produtos: Valor total dos produtos
            quantidade: Quantidade total de itens
            peso_kg: Peso total em kg
            distancia_km: Distância em km

        Returns:
            ResultadoCalculoPedido com breakdown dos valores
        """
        # Converter para Decimal para precisão
        valor_produtos_decimal = Decimal(str(valor_produtos))
        peso_kg_decimal = float(peso_kg)
        distancia_km_decimal = float(distancia_km)

        # Calcular desconto e frete
        desconto = Decimal(str(self._estrategia_desconto.calcular_desconto(
            float(valor_produtos_decimal), quantidade=quantidade
        )))

        frete = Decimal(str(self._estrategia_frete.calcular_frete(
            peso_kg=peso_kg_decimal, distancia_km=distancia_km_decimal
        )))

        # Calcular valor final
        valor_final = valor_produtos_decimal - desconto + frete

        return ResultadoCalculoPedido(
            valor_produtos=valor_produtos_decimal,
            desconto=desconto,
            frete=frete,
            valor_final=valor_final
        )

    def calcular_total_from_input(self, input_data: CalculoInput) -> ResultadoCalculoPedido:
        """
        Calcula o total do pedido a partir de um CalculoInput

        Args:
            input_data: Dados de entrada para cálculo

        Returns:
            ResultadoCalculoPedido com breakdown dos valores
        """
        return self.calcular_total(
            valor_produtos=input_data.valor_produtos,
            quantidade=input_data.quantidade,
            peso_kg=input_data.peso_kg,
            distancia_km=input_data.distancia_km
        )
