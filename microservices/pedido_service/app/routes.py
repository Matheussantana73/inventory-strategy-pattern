"""Rotas da API de pedidos"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
import httpx
import uuid
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from shared.database import get_db
from shared.redis_client import CacheService, EventBus

from .models import Pedido, ItemPedido, StatusPedido as StatusPedidoDB
from .schemas import (
    PedidoCreate,
    PedidoUpdate,
    PedidoResponse,
    PedidoListResponse,
    PedidoResumoResponse,
    RecalcularPedidoRequest,
    MessageResponse,
    StatusPedido,
)

router = APIRouter(prefix="/api/v1/pedidos", tags=["Pedidos"])

# Configuração
PRODUTO_SERVICE_URL = os.getenv("PRODUTO_SERVICE_URL", "http://produto-service:8001")
CALCULO_SERVICE_URL = os.getenv("CALCULO_SERVICE_URL", "http://calculo-service:8003")

# Serviços
cache = CacheService(prefix="pedido")
event_bus = EventBus()


async def obter_produto(produto_id: int) -> dict:
    """Obtém dados de um produto do serviço de produtos"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PRODUTO_SERVICE_URL}/api/v1/produtos/{produto_id}"
        )
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Produto {produto_id} não encontrado",
            )
        response.raise_for_status()
        return response.json()


async def calcular_valores(
    valor_produtos: float,
    quantidade: int,
    peso_kg: float,
    distancia_km: float,
    tipo_desconto: str,
    tipo_frete: str,
) -> dict:
    """Calcula valores usando o serviço de cálculo"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CALCULO_SERVICE_URL}/api/v1/calcular",
            json={
                "valor_produtos": valor_produtos,
                "quantidade": quantidade,
                "peso_kg": peso_kg,
                "distancia_km": distancia_km,
                "tipo_desconto": tipo_desconto,
                "tipo_frete": tipo_frete,
            },
        )
        response.raise_for_status()
        return response.json()


async def atualizar_estoque_produto(produto_id: int, quantidade: int):
    """Atualiza o estoque de um produto"""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{PRODUTO_SERVICE_URL}/api/v1/produtos/{produto_id}/estoque",
            json={"quantidade": quantidade, "operacao": "subtract"},
        )
        if response.status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para o produto {produto_id}",
            )
        response.raise_for_status()


def gerar_numero_pedido() -> str:
    """Gera número único para o pedido"""
    return f"PED-{uuid.uuid4().hex[:8].upper()}"


@router.get("", response_model=PedidoListResponse)
def listar_pedidos(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status_filter: Optional[StatusPedido] = Query(None, alias="status"),
    usuario_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Lista pedidos com paginação e filtros"""
    query = db.query(Pedido)

    if status_filter:
        query = query.filter(Pedido.status == status_filter.value)

    if usuario_id:
        query = query.filter(Pedido.usuario_id == usuario_id)

    total = query.count()
    offset = (page - 1) * per_page
    pedidos = (
        query.order_by(Pedido.created_at.desc()).offset(offset).limit(per_page).all()
    )

    return PedidoListResponse(
        items=[PedidoResumoResponse.model_validate(p) for p in pedidos],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obter_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Obtém um pedido pelo ID"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido com ID {pedido_id} não encontrado",
        )

    return pedido


@router.get("/numero/{numero}", response_model=PedidoResponse)
def obter_pedido_por_numero(numero: str, db: Session = Depends(get_db)):
    """Obtém um pedido pelo número"""
    pedido = db.query(Pedido).filter(Pedido.numero == numero).first()

    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido {numero} não encontrado",
        )

    return pedido


@router.post("", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
async def criar_pedido(pedido_data: PedidoCreate, db: Session = Depends(get_db)):
    """Cria um novo pedido"""
    # Criar pedido
    pedido = Pedido(
        numero=gerar_numero_pedido(),
        tipo_desconto=pedido_data.tipo_desconto.value,
        tipo_frete=pedido_data.tipo_frete.value,
        distancia_km=pedido_data.distancia_km,
        endereco_entrega=pedido_data.endereco_entrega,
        observacoes=pedido_data.observacoes,
    )
    db.add(pedido)
    db.flush()

    valor_total_produtos = Decimal("0")
    peso_total = 0
    quantidade_total = 0

    # Processar itens
    for item_data in pedido_data.itens:
        # Obter dados do produto
        produto = await obter_produto(item_data.produto_id)

        # Criar item
        subtotal = Decimal(str(produto["preco"])) * item_data.quantidade
        item = ItemPedido(
            pedido_id=pedido.id,
            produto_id=item_data.produto_id,
            nome_produto=produto["nome"],
            preco_unitario=Decimal(str(produto["preco"])),
            quantidade=item_data.quantidade,
            peso_unitario=produto.get("peso", 0),
            subtotal=subtotal,
        )
        db.add(item)

        # Acumular valores
        valor_total_produtos += subtotal
        peso_total += produto.get("peso", 0) * item_data.quantidade
        quantidade_total += item_data.quantidade

        # Atualizar estoque
        await atualizar_estoque_produto(item_data.produto_id, item_data.quantidade)

    # Calcular valores finais
    calculo = await calcular_valores(
        valor_produtos=float(valor_total_produtos),
        quantidade=quantidade_total,
        peso_kg=peso_total,
        distancia_km=pedido_data.distancia_km,
        tipo_desconto=pedido_data.tipo_desconto.value,
        tipo_frete=pedido_data.tipo_frete.value,
    )

    # Atualizar pedido com valores calculados
    pedido.valor_produtos = valor_total_produtos
    pedido.valor_desconto = Decimal(str(calculo["desconto"]))
    pedido.valor_frete = Decimal(str(calculo["frete"]))
    pedido.valor_total = Decimal(str(calculo["valor_final"]))
    pedido.peso_total = peso_total

    db.commit()
    db.refresh(pedido)

    # Publicar evento
    event_bus.publish(
        "pedido.criado",
        {
            "id": pedido.id,
            "numero": pedido.numero,
            "valor_total": float(pedido.valor_total),
        },
    )

    return pedido


@router.put("/{pedido_id}", response_model=PedidoResponse)
async def atualizar_pedido(
    pedido_id: int, pedido_data: PedidoUpdate, db: Session = Depends(get_db)
):
    """Atualiza um pedido"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido com ID {pedido_id} não encontrado",
        )

    # Verificar se pode ser alterado
    if pedido.status in [StatusPedidoDB.ENVIADO.value, StatusPedidoDB.ENTREGUE.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pedido já foi enviado/entregue e não pode ser alterado",
        )

    # Atualizar campos
    update_data = pedido_data.model_dump(exclude_unset=True)

    # Converter enums para valores
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value
    if "tipo_desconto" in update_data and update_data["tipo_desconto"]:
        update_data["tipo_desconto"] = update_data["tipo_desconto"].value
    if "tipo_frete" in update_data and update_data["tipo_frete"]:
        update_data["tipo_frete"] = update_data["tipo_frete"].value

    for field, value in update_data.items():
        setattr(pedido, field, value)

    # Recalcular se estratégias mudaram
    if any(k in update_data for k in ["tipo_desconto", "tipo_frete", "distancia_km"]):
        quantidade_total = sum(item.quantidade for item in pedido.itens)

        calculo = await calcular_valores(
            valor_produtos=float(pedido.valor_produtos),
            quantidade=quantidade_total,
            peso_kg=pedido.peso_total,
            distancia_km=pedido.distancia_km,
            tipo_desconto=pedido.tipo_desconto,
            tipo_frete=pedido.tipo_frete,
        )

        pedido.valor_desconto = Decimal(str(calculo["desconto"]))
        pedido.valor_frete = Decimal(str(calculo["frete"]))
        pedido.valor_total = Decimal(str(calculo["valor_final"]))

    db.commit()
    db.refresh(pedido)

    # Publicar evento
    event_bus.publish(
        "pedido.atualizado",
        {"id": pedido.id, "numero": pedido.numero, "status": pedido.status},
    )

    return pedido


@router.delete("/{pedido_id}", response_model=MessageResponse)
def cancelar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Cancela um pedido"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido com ID {pedido_id} não encontrado",
        )

    if pedido.status in [StatusPedidoDB.ENVIADO.value, StatusPedidoDB.ENTREGUE.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pedido já foi enviado/entregue e não pode ser cancelado",
        )

    pedido.status = StatusPedidoDB.CANCELADO.value
    db.commit()

    # Publicar evento
    event_bus.publish("pedido.cancelado", {"id": pedido.id, "numero": pedido.numero})

    return MessageResponse(message=f"Pedido {pedido.numero} cancelado com sucesso")


@router.post("/{pedido_id}/recalcular", response_model=PedidoResponse)
async def recalcular_pedido(
    pedido_id: int, request: RecalcularPedidoRequest, db: Session = Depends(get_db)
):
    """Recalcula valores do pedido com novas estratégias"""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido com ID {pedido_id} não encontrado",
        )

    # Atualizar estratégias se fornecidas
    if request.tipo_desconto:
        pedido.tipo_desconto = request.tipo_desconto.value
    if request.tipo_frete:
        pedido.tipo_frete = request.tipo_frete.value
    if request.distancia_km is not None:
        pedido.distancia_km = request.distancia_km

    # Recalcular
    quantidade_total = sum(item.quantidade for item in pedido.itens)

    calculo = await calcular_valores(
        valor_produtos=float(pedido.valor_produtos),
        quantidade=quantidade_total,
        peso_kg=pedido.peso_total,
        distancia_km=pedido.distancia_km,
        tipo_desconto=pedido.tipo_desconto,
        tipo_frete=pedido.tipo_frete,
    )

    pedido.valor_desconto = Decimal(str(calculo["desconto"]))
    pedido.valor_frete = Decimal(str(calculo["frete"]))
    pedido.valor_total = Decimal(str(calculo["valor_final"]))

    db.commit()
    db.refresh(pedido)

    return pedido
