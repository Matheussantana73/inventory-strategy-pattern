from abc import ABC, abstractmethod


class EstrategiaFrete(ABC):
    """Interface para estratégias de frete"""

    @abstractmethod
    def calcular_frete(self, **kwargs) -> float:
        """
        Calcula o valor do frete

        Returns:
            float: Valor do frete
        """
        pass


class FretePorPeso(EstrategiaFrete):
    """Frete calculado por peso"""

    def __init__(self, valor_por_kg: float):
        self.valor_por_kg = valor_por_kg

    def calcular_frete(self, peso_kg: float = 0, **kwargs) -> float:
        return peso_kg * self.valor_por_kg


class FretePorDistancia(EstrategiaFrete):
    """Frete calculado por distância"""

    def __init__(self, valor_por_km: float):
        self.valor_por_km = valor_por_km

    def calcular_frete(self, distancia_km: float = 0, **kwargs) -> float:
        return distancia_km * self.valor_por_km


class FreteFixo(EstrategiaFrete):
    """Frete com valor fixo"""

    def __init__(self, valor_fixo: float):
        self.valor_fixo = valor_fixo

    def calcular_frete(self, **kwargs) -> float:
        return self.valor_fixo


class FreteGratis(EstrategiaFrete):
    """Frete gratuito"""

    def calcular_frete(self, **kwargs) -> float:
        return 0.0
