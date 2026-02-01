from django.contrib import admin
from .models import Produto, Pedido, ItemPedido


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "peso", "quantidade_estoque")
    search_fields = ("nome",)
    list_filter = ("preco",)
    ordering = ("nome",)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1
    fields = ("produto", "quantidade", "preco_unitario")
    autocomplete_fields = ["produto"]


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "data_criacao",
        "get_tipo_desconto_display",
        "get_tipo_frete_display",
        "valor_total",
    )
    search_fields = ("numero",)
    list_filter = ("tipo_desconto", "tipo_frete", "data_criacao")
    readonly_fields = ("data_criacao", "valor_total")
    inlines = [ItemPedidoInline]
    fieldsets = (
        ("Informações do Pedido", {
            "fields": ("numero", "data_criacao", "valor_total")
        }),
        ("Estratégias", {
            "fields": ("tipo_desconto", "tipo_frete"),
            "description": "Selecione as estratégias de desconto e frete para este pedido"
        }),
    )

    def get_tipo_desconto_display(self, obj):
        """Exibe o tipo de desconto formatado"""
        return obj.get_tipo_desconto_display()
    get_tipo_desconto_display.short_description = "Desconto"

    def get_tipo_frete_display(self, obj):
        """Exibe o tipo de frete formatado"""
        return obj.get_tipo_frete_display()
    get_tipo_frete_display.short_description = "Frete"


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "produto", "quantidade", "preco_unitario", "subtotal")
    search_fields = ("pedido__numero", "produto__nome")
    list_filter = ("pedido",)
    autocomplete_fields = ["produto"]

    def subtotal(self, obj):
        """Calcula o subtotal do item"""
        return f"R$ {obj.quantidade * obj.preco_unitario:.2f}"
    subtotal.short_description = "Subtotal"
    list_filter = ("pedido",)
