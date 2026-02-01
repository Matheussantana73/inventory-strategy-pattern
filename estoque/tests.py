"""Testes unitários para o sistema de estoque com padrão Strategy"""
from decimal import Decimal
from django.test import TestCase

from estoque.calculadora_pedido import CalculadoraPedido
from estoque.schemas import ResultadoCalculoPedido, CalculoInput
from estoque.strategies.desconto import (
    DescontoPercentual,
    DescontoFixo,
    DescontoProgressivo,
    SemDesconto,
)
from estoque.strategies.frete import (
    FretePorPeso,
    FretePorDistancia,
    FreteFixo,
    FreteGratis,
)


class TestEstrategiaDesconto(TestCase):
    """Testes para estratégias de desconto"""

    def test_desconto_percentual(self):
        """Testa desconto percentual"""
        desconto = DescontoPercentual(10)
        resultado = desconto.calcular_desconto(1000)
        self.assertEqual(resultado, 100)

    def test_desconto_percentual_zero(self):
        """Testa desconto percentual com valor zero"""
        desconto = DescontoPercentual(0)
        resultado = desconto.calcular_desconto(1000)
        self.assertEqual(resultado, 0)

    def test_desconto_fixo(self):
        """Testa desconto fixo"""
        desconto = DescontoFixo(50)
        resultado = desconto.calcular_desconto(1000)
        self.assertEqual(resultado, 50)

    def test_desconto_fixo_maior_que_valor(self):
        """Testa desconto fixo maior que o valor do produto"""
        desconto = DescontoFixo(1500)
        resultado = desconto.calcular_desconto(1000)
        self.assertEqual(resultado, 1000)  # Não pode ser maior que o valor

    def test_desconto_progressivo(self):
        """Testa desconto progressivo"""
        desconto = DescontoProgressivo({100: 5, 500: 10, 1000: 15})
        resultado = desconto.calcular_desconto(1000, quantidade=600)
        self.assertEqual(resultado, 100)  # 10% de 1000

    def test_desconto_progressivo_faixa_maxima(self):
        """Testa desconto progressivo na faixa máxima"""
        desconto = DescontoProgressivo({100: 5, 500: 10, 1000: 15})
        resultado = desconto.calcular_desconto(2000, quantidade=1500)
        self.assertEqual(resultado, 300)  # 15% de 2000

    def test_sem_desconto(self):
        """Testa estratégia sem desconto"""
        desconto = SemDesconto()
        resultado = desconto.calcular_desconto(1000)
        self.assertEqual(resultado, 0)


class TestEstrategiaFrete(TestCase):
    """Testes para estratégias de frete"""

    def test_frete_por_peso(self):
        """Testa frete por peso"""
        frete = FretePorPeso(valor_por_kg=5)
        resultado = frete.calcular_frete(peso_kg=10)
        self.assertEqual(resultado, 50)

    def test_frete_por_peso_zero(self):
        """Testa frete por peso com peso zero"""
        frete = FretePorPeso(valor_por_kg=5)
        resultado = frete.calcular_frete(peso_kg=0)
        self.assertEqual(resultado, 0)

    def test_frete_por_distancia(self):
        """Testa frete por distância"""
        frete = FretePorDistancia(valor_por_km=2)
        resultado = frete.calcular_frete(distancia_km=100)
        self.assertEqual(resultado, 200)

    def test_frete_fixo(self):
        """Testa frete fixo"""
        frete = FreteFixo(valor_fixo=50)
        resultado = frete.calcular_frete()
        self.assertEqual(resultado, 50)

    def test_frete_gratis(self):
        """Testa frete grátis"""
        frete = FreteGratis()
        resultado = frete.calcular_frete()
        self.assertEqual(resultado, 0)


class TestCalculadoraPedido(TestCase):
    """Testes para a calculadora de pedidos"""

    def test_calculo_com_desconto_e_frete(self):
        """Testa cálculo completo com desconto e frete"""
        desconto = DescontoPercentual(10)
        frete = FreteFixo(50)
        calculadora = CalculadoraPedido(desconto, frete)

        resultado = calculadora.calcular_total(1000)

        self.assertIsInstance(resultado, ResultadoCalculoPedido)
        self.assertEqual(resultado.valor_produtos, Decimal("1000"))
        self.assertEqual(resultado.desconto, Decimal("100"))
        self.assertEqual(resultado.frete, Decimal("50"))
        self.assertEqual(resultado.valor_final, Decimal("950"))

    def test_troca_dinamica_estrategia(self):
        """Testa troca dinâmica de estratégia"""
        desconto = DescontoPercentual(10)
        frete = FreteFixo(50)
        calculadora = CalculadoraPedido(desconto, frete)

        # Trocar estratégia
        calculadora.set_estrategia_desconto(DescontoFixo(100))
        resultado = calculadora.calcular_total(1000)

        self.assertEqual(resultado.desconto, Decimal("100"))
        self.assertEqual(resultado.valor_final, Decimal("950"))

    def test_calcular_total_from_input(self):
        """Testa cálculo usando CalculoInput"""
        desconto = DescontoPercentual(15)
        frete = FretePorPeso(valor_por_kg=5)
        calculadora = CalculadoraPedido(desconto, frete)

        input_data = CalculoInput(
            valor_produtos=Decimal("2000"),
            quantidade=10,
            peso_kg=Decimal("20"),
            distancia_km=Decimal("0")
        )

        resultado = calculadora.calcular_total_from_input(input_data)

        self.assertEqual(resultado.valor_produtos, Decimal("2000"))
        self.assertEqual(resultado.desconto, Decimal("300"))  # 15% de 2000
        self.assertEqual(resultado.frete, Decimal("100"))  # 20kg * 5
        self.assertEqual(resultado.valor_final, Decimal("1800"))  # 2000 - 300 + 100

    def test_percentual_desconto(self):
        """Testa propriedade de percentual de desconto"""
        desconto = DescontoFixo(250)
        frete = FreteFixo(50)
        calculadora = CalculadoraPedido(desconto, frete)

        resultado = calculadora.calcular_total(1000)

        self.assertEqual(resultado.percentual_desconto, 25.0)  # 250/1000 * 100

    def test_calculo_com_decimal(self):
        """Testa cálculo com valores Decimal"""
        desconto = DescontoPercentual(10)
        frete = FreteFixo(50)
        calculadora = CalculadoraPedido(desconto, frete)

        resultado = calculadora.calcular_total(
            valor_produtos=Decimal("1234.56"),
            quantidade=5,
            peso_kg=Decimal("10.5")
        )

        self.assertEqual(resultado.valor_produtos, Decimal("1234.56"))
        self.assertAlmostEqual(float(resultado.desconto), 123.456, places=2)


class TestSchemas(TestCase):
    """Testes para schemas Pydantic"""

    def test_resultado_calculo_pedido_valido(self):
        """Testa criação de ResultadoCalculoPedido válido"""
        resultado = ResultadoCalculoPedido(
            valor_produtos=Decimal("1000"),
            desconto=Decimal("100"),
            frete=Decimal("50"),
            valor_final=Decimal("950")
        )

        self.assertEqual(resultado.valor_produtos, Decimal("1000"))
        self.assertEqual(resultado.percentual_desconto, 10.0)

    def test_calculo_input_valido(self):
        """Testa criação de CalculoInput válido"""
        input_data = CalculoInput(
            valor_produtos=Decimal("500"),
            quantidade=5,
            peso_kg=Decimal("10"),
            distancia_km=Decimal("100")
        )

        self.assertEqual(input_data.valor_produtos, Decimal("500"))
        self.assertEqual(input_data.quantidade, 5)
