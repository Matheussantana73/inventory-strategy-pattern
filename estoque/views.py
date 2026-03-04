"""Views do sistema de estoque com padrão Strategy"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from decimal import Decimal

from estoque.models import Pedido, ItemPedido, Produto
from estoque.calculadora_pedido import CalculadoraPedido
from estoque.schemas import ResultadoCalculoPedido
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


# Mapeamento de estratégias disponíveis
ESTRATEGIAS_DESCONTO = {
    "percentual_10": lambda: DescontoPercentual(10),
    "percentual_15": lambda: DescontoPercentual(50),
    "percentual_20": lambda: DescontoPercentual(20),
    "percentual_30": lambda: DescontoPercentual(30),
    "fixo_50": lambda: DescontoFixo(50),
    "fixo_100": lambda: DescontoFixo(100),
    "progressivo": lambda: DescontoProgressivo({100: 5, 500: 10, 1000: 15}),
    "sem_desconto": lambda: SemDesconto(),
}

ESTRATEGIAS_FRETE = {
    "por_peso": lambda: FretePorPeso(valor_por_kg=5),
    "por_distancia": lambda: FretePorDistancia(valor_por_km=2),
    "fixo_50": lambda: FreteFixo(50),
    "fixo_30": lambda: FreteFixo(30),
    "gratis": lambda: FreteGratis(),
}


def _pydantic_to_json(resultado: ResultadoCalculoPedido) -> dict:
    """
    Converte um modelo Pydantic para dict JSON-serializável

    Args:
        resultado: Resultado do cálculo do pedido

    Returns:
        Dict com valores serializáveis
    """
    return {
        "valor_produtos": float(resultado.valor_produtos),
        "desconto": float(resultado.desconto),
        "frete": float(resultado.frete),
        "valor_final": float(resultado.valor_final),
        "percentual_desconto": resultado.percentual_desconto,
    }


@require_http_methods(["GET"])
def criar_pedido(request):
    """
    Exemplo de criação de pedido com estratégias específicas

    Returns:
        JsonResponse com resultado do cálculo
    """
    # Exemplo: Cliente com desconto de 10% e frete fixo de R$ 50
    estrategia_desconto = DescontoPercentual(percentual=10)
    estrategia_frete = FreteFixo(valor_fixo=50)

    calculadora = CalculadoraPedido(estrategia_desconto, estrategia_frete)

    # Simular cálculo
    resultado = calculadora.calcular_total(
        valor_produtos=1000, quantidade=5, peso_kg=10
    )

    return JsonResponse(_pydantic_to_json(resultado))


@require_http_methods(["GET"])
def calcular_pedido_dinamico(request, pedido_id: int):
    """
    Calcula pedido com estratégias dinâmicas baseadas na configuração do pedido

    Args:
        request: Request HTTP
        pedido_id: ID do pedido a calcular

    Returns:
        JsonResponse com resultado do cálculo
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Obter estratégias do pedido
    desconto = ESTRATEGIAS_DESCONTO.get(pedido.tipo_desconto, lambda: SemDesconto())()
    frete = ESTRATEGIAS_FRETE.get(pedido.tipo_frete, lambda: FreteFixo(50))()

    calculadora = CalculadoraPedido(desconto, frete)

    # Calcular valores dos itens
    valor_total = sum(
        item.quantidade * item.preco_unitario for item in pedido.itens.all()
    )
    peso_total = sum(item.produto.peso * item.quantidade for item in pedido.itens.all())
    quantidade_total = sum(item.quantidade for item in pedido.itens.all())

    resultado = calculadora.calcular_total(
        valor_produtos=float(valor_total),
        quantidade=quantidade_total,
        peso_kg=peso_total,
    )

    # Atualizar valor total do pedido
    pedido.valor_total = resultado.valor_final
    pedido.save(update_fields=["valor_total"])

    return JsonResponse(
        {
            **_pydantic_to_json(resultado),
            "pedido_numero": pedido.numero,
            "itens_count": quantidade_total,
        }
    )


# ======================
# Views para Interface Web
# ======================


@require_http_methods(["GET"])
def home(request):
    """Página inicial do sistema"""
    return render(request, "estoque/home.html")


@require_http_methods(["GET"])
def testar_estrategias(request):
    """Página para testar diferentes estratégias"""
    return render(request, "estoque/testar_estrategias.html")


@require_http_methods(["GET"])
def calcular_estrategias_api(request):
    """
    API para calcular valores com diferentes estratégias

    Parâmetros GET:
        - valor_produtos: float
        - quantidade: int
        - peso_kg: float
        - distancia_km: float
        - tipo_desconto: str
        - tipo_frete: str
    """
    try:
        # Obter parâmetros
        valor_produtos = float(request.GET.get("valor_produtos", 0))
        quantidade = int(request.GET.get("quantidade", 0))
        peso_kg = float(request.GET.get("peso_kg", 0))
        distancia_km = float(request.GET.get("distancia_km", 0))
        tipo_desconto = request.GET.get("tipo_desconto", "sem_desconto")
        tipo_frete = request.GET.get("tipo_frete", "fixo_50")

        # Obter estratégias
        desconto = ESTRATEGIAS_DESCONTO.get(tipo_desconto, lambda: SemDesconto())()
        frete = ESTRATEGIAS_FRETE.get(tipo_frete, lambda: FreteFixo(50))()

        # Calcular
        calculadora = CalculadoraPedido(desconto, frete)
        resultado = calculadora.calcular_total(
            valor_produtos=valor_produtos,
            quantidade=quantidade,
            peso_kg=peso_kg,
            distancia_km=distancia_km,
        )

        return JsonResponse(_pydantic_to_json(resultado))

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["GET", "POST"])
def criar_pedido_form(request):
    """Formulário para criar pedido"""
    if request.method == "POST":
        try:
            # Obter dados do formulário
            numero = request.POST.get("numero")
            tipo_desconto = request.POST.get("tipo_desconto")
            tipo_frete = request.POST.get("tipo_frete")
            distancia_km = float(request.POST.get("distancia_km", 0))

            # Verificar se pedido já existe
            if Pedido.objects.filter(numero=numero).exists():
                messages.error(request, f"Pedido {numero} já existe!")
                return redirect("criar_pedido_form")

            # Criar pedido
            pedido = Pedido.objects.create(
                numero=numero,
                tipo_desconto=tipo_desconto,
                tipo_frete=tipo_frete,
            )

            # Adicionar itens
            produto_ids = request.POST.getlist("produto_id[]")
            quantidades = request.POST.getlist("quantidade[]")

            valor_total_produtos = Decimal("0")
            peso_total = 0
            quantidade_total = 0

            for produto_id, quantidade_str in zip(produto_ids, quantidades):
                if produto_id and quantidade_str:
                    produto = Produto.objects.get(id=produto_id)
                    quantidade = int(quantidade_str)

                    # Verificar estoque
                    if quantidade > produto.quantidade_estoque:
                        pedido.delete()
                        messages.error(
                            request,
                            f"Quantidade insuficiente para {produto.nome}! Estoque: {produto.quantidade_estoque}",
                        )
                        return redirect("criar_pedido_form")

                    # Criar item
                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=produto.preco,
                    )

                    # Atualizar estoque
                    produto.quantidade_estoque -= quantidade
                    produto.save()

                    # Acumular valores
                    valor_total_produtos += produto.preco * quantidade
                    peso_total += produto.peso * quantidade
                    quantidade_total += quantidade

            # Calcular valor final com estratégias
            desconto = ESTRATEGIAS_DESCONTO.get(tipo_desconto, lambda: SemDesconto())()
            frete = ESTRATEGIAS_FRETE.get(tipo_frete, lambda: FreteFixo(50))()

            calculadora = CalculadoraPedido(desconto, frete)
            resultado = calculadora.calcular_total(
                valor_produtos=float(valor_total_produtos),
                quantidade=quantidade_total,
                peso_kg=peso_total,
                distancia_km=distancia_km,
            )

            # Salvar valor total
            pedido.valor_total = resultado.valor_final
            pedido.save()

            messages.success(
                request,
                f"Pedido {numero} criado com sucesso! Valor total: R$ {resultado.valor_final}",
            )
            return redirect("detalhes_pedido", pedido_id=pedido.id)

        except Exception as e:
            messages.error(request, f"Erro ao criar pedido: {str(e)}")
            return redirect("criar_pedido_form")

    # GET - mostrar formulário
    produtos = Produto.objects.filter(quantidade_estoque__gt=0)
    return render(request, "estoque/criar_pedido.html", {"produtos": produtos})


@require_http_methods(["GET"])
def listar_pedidos(request):
    """Lista todos os pedidos"""
    pedidos = Pedido.objects.all().order_by("-data_criacao")
    return render(request, "estoque/listar_pedidos.html", {"pedidos": pedidos})


@require_http_methods(["GET"])
def detalhes_pedido(request, pedido_id):
    """Detalhes de um pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Calcular valores detalhados
    valor_total_produtos = sum(
        item.quantidade * item.preco_unitario for item in pedido.itens.all()
    )
    peso_total = sum(item.produto.peso * item.quantidade for item in pedido.itens.all())
    quantidade_total = sum(item.quantidade for item in pedido.itens.all())

    # Obter estratégias
    desconto = ESTRATEGIAS_DESCONTO.get(pedido.tipo_desconto, lambda: SemDesconto())()
    frete = ESTRATEGIAS_FRETE.get(pedido.tipo_frete, lambda: FreteFixo(50))()

    # Calcular
    calculadora = CalculadoraPedido(desconto, frete)
    resultado = calculadora.calcular_total(
        valor_produtos=float(valor_total_produtos),
        quantidade=quantidade_total,
        peso_kg=peso_total,
    )

    return render(
        request,
        "estoque/detalhes_pedido.html",
        {"pedido": pedido, "calculo": resultado},
    )
