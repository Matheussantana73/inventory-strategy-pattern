from abc import ABC, abstractmethod


class EstrategiaDesconto(ABC):
    """Interface para estratégias de desconto"""

    @abstractmethod
    def calcular_desconto(self, valor: float, **kwargs) -> float:
        """
        Calcula o desconto sobre um valor

        Args:
            valor: Valor base para cálculo
            **kwargs: Parâmetros adicionais específicos da estratégia

        Returns:
            float: Valor do desconto
        """
        pass


class DescontoPercentual(EstrategiaDesconto):
    """Desconto em percentual"""

    def __init__(self, percentual: float):
        self.percentual = percentual

    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return valor * (self.percentual / 100)


class DescontoFixo(EstrategiaDesconto):
    """Desconto em valor fixo"""

    def __init__(self, valor_desconto: float):
        self.valor_desconto = valor_desconto

    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return min(self.valor_desconto, valor)


class DescontoProgressivo(EstrategiaDesconto):
    """Desconto progressivo baseado na quantidade"""

    def __init__(self, faixas: dict):
        # faixas = {100: 5, 500: 10, 1000: 15}
        # Acima de 100 unidades: 5%, acima de 500: 10%, etc
        self.faixas = faixas

    def calcular_desconto(self, valor: float, quantidade: int = 0, **kwargs) -> float:
        percentual = 0
        for quantidade_minima, perc in sorted(self.faixas.items()):
            if quantidade >= quantidade_minima:
                percentual = perc
        return valor * (percentual / 100)


class SemDesconto(EstrategiaDesconto):
    """Sem desconto"""

    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return 0.0
