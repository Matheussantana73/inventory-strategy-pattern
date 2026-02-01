from django.db import models
from estoque.strategies.desconto import EstrategiaDesconto, DescontoPercentual
from estoque.strategies.frete import EstrategiaFrete, FreteFixo


class Produto(models.Model):
    nome = models.CharField(max_length=200)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    peso = models.FloatField(default=0)
    quantidade_estoque = models.IntegerField(default=0)

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    """Modelo de pedido com estratégias de desconto e frete"""

    class TipoDesconto(models.TextChoices):
        """Choices para tipos de desconto disponíveis"""
        PERCENTUAL_10 = "percentual_10", "Desconto de 10%"
        PERCENTUAL_15 = "percentual_15", "Desconto de 15%"
        PERCENTUAL_20 = "percentual_20", "Desconto de 20%"
        FIXO_50 = "fixo_50", "Desconto fixo de R$ 50"
        FIXO_100 = "fixo_100", "Desconto fixo de R$ 100"
        PROGRESSIVO = "progressivo", "Desconto progressivo por quantidade"
        SEM_DESCONTO = "sem_desconto", "Sem desconto"

    class TipoFrete(models.TextChoices):
        """Choices para tipos de frete disponíveis"""
        POR_PESO = "por_peso", "Frete por peso (R$ 5/kg)"
        POR_DISTANCIA = "por_distancia", "Frete por distância (R$ 2/km)"
        FIXO_30 = "fixo_30", "Frete fixo de R$ 30"
        FIXO_50 = "fixo_50", "Frete fixo de R$ 50"
        GRATIS = "gratis", "Frete grátis"

    numero = models.CharField(max_length=50, unique=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Estratégias (armazenadas como choices para persistência)
    tipo_desconto = models.CharField(
        max_length=50,
        choices=TipoDesconto.choices,
        default=TipoDesconto.SEM_DESCONTO,
        verbose_name="Tipo de Desconto",
        help_text="Estratégia de desconto aplicada ao pedido"
    )
    tipo_frete = models.CharField(
        max_length=50,
        choices=TipoFrete.choices,
        default=TipoFrete.FIXO_50,
        verbose_name="Tipo de Frete",
        help_text="Estratégia de frete aplicada ao pedido"
    )

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"Pedido {self.numero}"

    def get_tipo_desconto_display_custom(self):
        """Retorna descrição customizada do tipo de desconto"""
        return self.get_tipo_desconto_display()

    def get_tipo_frete_display_custom(self):
        """Retorna descrição customizada do tipo de frete"""
        return self.get_tipo_frete_display()


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produto.nome} x{self.quantidade}"
