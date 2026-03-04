"""Estratégias de Frete - Padrão Strategy"""

from abc import ABC, abstractmethod


class EstrategiaFrete(ABC):
    """Interface para estratégias de frete"""

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome da estratégia"""
        pass

    @property
    @abstractmethod
    def descricao(self) -> str:
        """Descrição da estratégia"""
        pass

    @abstractmethod
    def calcular_frete(self, **kwargs) -> float:
        """
        Calcula o valor do frete

        Args:
            **kwargs: Parâmetros específicos da estratégia
                      (peso_kg, distancia_km, etc)

        Returns:
            float: Valor do frete
        """
        pass


class FretePorPeso(EstrategiaFrete):
    """Frete calculado por peso"""

    def __init__(self, valor_por_kg: float):
        self.valor_por_kg = valor_por_kg

    @property
    def nome(self) -> str:
        return "por_peso"

    @property
    def descricao(self) -> str:
        return f"Frete por peso (R$ {self.valor_por_kg:.2f}/kg)"

    def calcular_frete(self, peso_kg: float = 0, **kwargs) -> float:
        return peso_kg * self.valor_por_kg


class FretePorDistancia(EstrategiaFrete):
    """Frete calculado por distância"""

    def __init__(self, valor_por_km: float):
        self.valor_por_km = valor_por_km

    @property
    def nome(self) -> str:
        return "por_distancia"

    @property
    def descricao(self) -> str:
        return f"Frete por distância (R$ {self.valor_por_km:.2f}/km)"

    def calcular_frete(self, distancia_km: float = 0, **kwargs) -> float:
        return distancia_km * self.valor_por_km


class FretePorPesoDistancia(EstrategiaFrete):
    """Frete calculado por peso e distância combinados"""

    def __init__(self, valor_por_kg: float, valor_por_km: float):
        self.valor_por_kg = valor_por_kg
        self.valor_por_km = valor_por_km

    @property
    def nome(self) -> str:
        return "peso_distancia"

    @property
    def descricao(self) -> str:
        return f"Frete por peso + distância (R$ {self.valor_por_kg:.2f}/kg + R$ {self.valor_por_km:.2f}/km)"

    def calcular_frete(
        self, peso_kg: float = 0, distancia_km: float = 0, **kwargs
    ) -> float:
        return (peso_kg * self.valor_por_kg) + (distancia_km * self.valor_por_km)


class FreteFixo(EstrategiaFrete):
    """Frete com valor fixo"""

    def __init__(self, valor_fixo: float):
        self.valor_fixo = valor_fixo

    @property
    def nome(self) -> str:
        return f"fixo_{int(self.valor_fixo)}"

    @property
    def descricao(self) -> str:
        return f"Frete fixo de R$ {self.valor_fixo:.2f}"

    def calcular_frete(self, **kwargs) -> float:
        return self.valor_fixo


class FreteGratis(EstrategiaFrete):
    """Frete gratuito"""

    @property
    def nome(self) -> str:
        return "gratis"

    @property
    def descricao(self) -> str:
        return "Frete grátis"

    def calcular_frete(self, **kwargs) -> float:
        return 0.0


class FreteCondicional(EstrategiaFrete):
    """Frete grátis acima de determinado valor"""

    def __init__(self, valor_minimo: float, frete_padrao: float):
        self.valor_minimo = valor_minimo
        self.frete_padrao = frete_padrao

    @property
    def nome(self) -> str:
        return "condicional"

    @property
    def descricao(self) -> str:
        return f"Frete grátis acima de R$ {self.valor_minimo:.2f}"

    def calcular_frete(self, valor_produtos: float = 0, **kwargs) -> float:
        if valor_produtos >= self.valor_minimo:
            return 0.0
        return self.frete_padrao


# Registro de estratégias disponíveis
ESTRATEGIAS_FRETE = {
    "por_peso": lambda: FretePorPeso(valor_por_kg=5.0),
    "por_distancia": lambda: FretePorDistancia(valor_por_km=2.0),
    "peso_distancia": lambda: FretePorPesoDistancia(valor_por_kg=3.0, valor_por_km=1.5),
    "fixo_30": lambda: FreteFixo(30),
    "fixo_50": lambda: FreteFixo(50),
    "gratis": lambda: FreteGratis(),
    "condicional": lambda: FreteCondicional(valor_minimo=500, frete_padrao=30),
}


def obter_estrategia_frete(tipo: str) -> EstrategiaFrete:
    """Obtém estratégia de frete pelo tipo"""
    factory = ESTRATEGIAS_FRETE.get(tipo, lambda: FreteFixo(50))
    return factory()


def listar_estrategias_frete() -> list[dict]:
    """Lista todas as estratégias de frete disponíveis"""
    resultado = []
    for tipo, factory in ESTRATEGIAS_FRETE.items():
        estrategia = factory()
        resultado.append(
            {"tipo": tipo, "nome": estrategia.nome, "descricao": estrategia.descricao}
        )
    return resultado
