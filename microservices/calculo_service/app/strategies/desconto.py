"""Estratégias de Desconto - Padrão Strategy"""

from abc import ABC, abstractmethod
from decimal import Decimal


class EstrategiaDesconto(ABC):
    """Interface para estratégias de desconto"""

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
    def calcular_desconto(self, valor: float, **kwargs) -> float:
        """
        Calcula o desconto sobre um valor

        Args:
            valor: Valor base para cálculo
            **kwargs: Parâmetros adicionais (ex: quantidade)

        Returns:
            float: Valor do desconto
        """
        pass


class DescontoPercentual(EstrategiaDesconto):
    """Desconto em percentual sobre o valor"""

    def __init__(self, percentual: float):
        self.percentual = percentual

    @property
    def nome(self) -> str:
        return f"percentual_{int(self.percentual)}"

    @property
    def descricao(self) -> str:
        return f"Desconto de {self.percentual}%"

    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return valor * (self.percentual / 100)


class DescontoFixo(EstrategiaDesconto):
    """Desconto em valor fixo"""

    def __init__(self, valor_desconto: float):
        self.valor_desconto = valor_desconto

    @property
    def nome(self) -> str:
        return f"fixo_{int(self.valor_desconto)}"

    @property
    def descricao(self) -> str:
        return f"Desconto fixo de R$ {self.valor_desconto:.2f}"

    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return min(self.valor_desconto, valor)


class DescontoProgressivo(EstrategiaDesconto):
    """Desconto progressivo baseado na quantidade"""

    def __init__(self, faixas: dict[int, float]):
        """
        Args:
            faixas: Dict com quantidade mínima como chave e percentual como valor
                    Ex: {100: 5, 500: 10, 1000: 15}
        """
        self.faixas = faixas

    @property
    def nome(self) -> str:
        return "progressivo"

    @property
    def descricao(self) -> str:
        faixas_str = ", ".join(
            [f"{q}+ itens: {p}%" for q, p in sorted(self.faixas.items())]
        )
        return f"Desconto progressivo ({faixas_str})"

    def calcular_desconto(self, valor: float, quantidade: int = 0, **kwargs) -> float:
        percentual = 0
        for quantidade_minima, perc in sorted(self.faixas.items()):
            if quantidade >= quantidade_minima:
                percentual = perc
        return valor * (percentual / 100)


class DescontoPorValor(EstrategiaDesconto):
    """Desconto baseado no valor total da compra"""

    def __init__(self, faixas: dict[float, float]):
        """
        Args:
            faixas: Dict com valor mínimo como chave e percentual como valor
                    Ex: {500: 5, 1000: 10, 2000: 15}
        """
        self.faixas = faixas

    @property
    def nome(self) -> str:
        return "por_valor"

    @property
    def descricao(self) -> str:
        faixas_str = ", ".join(
            [f"R${v}+: {p}%" for v, p in sorted(self.faixas.items())]
        )
        return f"Desconto por valor ({faixas_str})"

    def calcular_desconto(self, valor: float, **kwargs) -> float:
        percentual = 0
        for valor_minimo, perc in sorted(self.faixas.items()):
            if valor >= valor_minimo:
                percentual = perc
        return valor * (percentual / 100)


class SemDesconto(EstrategiaDesconto):
    """Sem desconto aplicado"""

    @property
    def nome(self) -> str:
        return "sem_desconto"

    @property
    def descricao(self) -> str:
        return "Sem desconto"

    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return 0.0


# Registro de estratégias disponíveis
ESTRATEGIAS_DESCONTO = {
    "percentual_10": lambda: DescontoPercentual(10),
    "percentual_15": lambda: DescontoPercentual(15),
    "percentual_20": lambda: DescontoPercentual(20),
    "percentual_30": lambda: DescontoPercentual(30),
    "fixo_50": lambda: DescontoFixo(50),
    "fixo_100": lambda: DescontoFixo(100),
    "progressivo": lambda: DescontoProgressivo({10: 5, 50: 10, 100: 15, 200: 20}),
    "por_valor": lambda: DescontoPorValor({500: 5, 1000: 10, 2000: 15}),
    "sem_desconto": lambda: SemDesconto(),
}


def obter_estrategia_desconto(tipo: str) -> EstrategiaDesconto:
    """Obtém estratégia de desconto pelo tipo"""
    factory = ESTRATEGIAS_DESCONTO.get(tipo, lambda: SemDesconto())
    return factory()


def listar_estrategias_desconto() -> list[dict]:
    """Lista todas as estratégias de desconto disponíveis"""
    resultado = []
    for tipo, factory in ESTRATEGIAS_DESCONTO.items():
        estrategia = factory()
        resultado.append(
            {"tipo": tipo, "nome": estrategia.nome, "descricao": estrategia.descricao}
        )
    return resultado
