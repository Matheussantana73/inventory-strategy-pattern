"""Rotas da API de produtos"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from shared.database import get_db
from shared.redis_client import CacheService, EventBus

from .models import Produto
from .schemas import (
    ProdutoCreate,
    ProdutoUpdate,
    ProdutoResponse,
    ProdutoListResponse,
    EstoqueUpdate,
    MessageResponse,
)

router = APIRouter(prefix="/api/v1/produtos", tags=["Produtos"])

# Serviços
cache = CacheService(prefix="produto")
event_bus = EventBus()


@router.get("", response_model=ProdutoListResponse)
def listar_produtos(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Busca por nome ou SKU"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    apenas_disponiveis: bool = Query(False, description="Apenas produtos com estoque"),
    db: Session = Depends(get_db),
):
    """Lista produtos com paginação e filtros"""
    query = db.query(Produto).filter(Produto.ativo == 1)

    # Filtros
    if search:
        query = query.filter(
            or_(Produto.nome.ilike(f"%{search}%"), Produto.sku.ilike(f"%{search}%"))
        )

    if categoria:
        query = query.filter(Produto.categoria == categoria)

    if apenas_disponiveis:
        query = query.filter(Produto.quantidade_estoque > 0)

    # Contagem total
    total = query.count()

    # Paginação
    offset = (page - 1) * per_page
    produtos = query.offset(offset).limit(per_page).all()

    return ProdutoListResponse(
        items=produtos,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """Obtém um produto pelo ID"""
    # Tentar buscar do cache
    cached = cache.get(f"id:{produto_id}")
    if cached:
        return ProdutoResponse(**cached)

    # Buscar do banco
    produto = (
        db.query(Produto).filter(Produto.id == produto_id, Produto.ativo == 1).first()
    )

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não encontrado",
        )

    # Salvar no cache
    response = ProdutoResponse.model_validate(produto)
    cache.set(f"id:{produto_id}", response.model_dump(mode="json"))

    return response


@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(produto_data: ProdutoCreate, db: Session = Depends(get_db)):
    """Cria um novo produto"""
    # Verificar SKU único
    if produto_data.sku:
        existente = db.query(Produto).filter(Produto.sku == produto_data.sku).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SKU '{produto_data.sku}' já está em uso",
            )

    # Criar produto
    produto = Produto(**produto_data.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)

    # Publicar evento
    event_bus.publish(
        "produto.criado",
        {"id": produto.id, "nome": produto.nome, "preco": float(produto.preco)},
    )

    return produto


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int, produto_data: ProdutoUpdate, db: Session = Depends(get_db)
):
    """Atualiza um produto existente"""
    produto = (
        db.query(Produto).filter(Produto.id == produto_id, Produto.ativo == 1).first()
    )

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não encontrado",
        )

    # Verificar SKU único se estiver sendo alterado
    if produto_data.sku and produto_data.sku != produto.sku:
        existente = (
            db.query(Produto)
            .filter(Produto.sku == produto_data.sku, Produto.id != produto_id)
            .first()
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SKU '{produto_data.sku}' já está em uso",
            )

    # Atualizar campos
    update_data = produto_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(produto, field, value)

    db.commit()
    db.refresh(produto)

    # Invalidar cache
    cache.delete(f"id:{produto_id}")

    # Publicar evento
    event_bus.publish(
        "produto.atualizado",
        {"id": produto.id, "campos_alterados": list(update_data.keys())},
    )

    return produto


@router.delete("/{produto_id}", response_model=MessageResponse)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Deleta (desativa) um produto"""
    produto = (
        db.query(Produto).filter(Produto.id == produto_id, Produto.ativo == 1).first()
    )

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não encontrado",
        )

    # Soft delete
    produto.ativo = 0
    db.commit()

    # Invalidar cache
    cache.delete(f"id:{produto_id}")

    # Publicar evento
    event_bus.publish("produto.deletado", {"id": produto_id})

    return MessageResponse(message=f"Produto {produto_id} deletado com sucesso")


@router.put("/{produto_id}/estoque", response_model=ProdutoResponse)
def atualizar_estoque(
    produto_id: int, estoque_data: EstoqueUpdate, db: Session = Depends(get_db)
):
    """Atualiza o estoque de um produto"""
    produto = (
        db.query(Produto).filter(Produto.id == produto_id, Produto.ativo == 1).first()
    )

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {produto_id} não encontrado",
        )

    # Aplicar operação
    if estoque_data.operacao == "set":
        produto.quantidade_estoque = estoque_data.quantidade
    elif estoque_data.operacao == "add":
        produto.quantidade_estoque += estoque_data.quantidade
    elif estoque_data.operacao == "subtract":
        nova_quantidade = produto.quantidade_estoque - estoque_data.quantidade
        if nova_quantidade < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {produto.quantidade_estoque}",
            )
        produto.quantidade_estoque = nova_quantidade
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Operação inválida: {estoque_data.operacao}",
        )

    db.commit()
    db.refresh(produto)

    # Invalidar cache
    cache.delete(f"id:{produto_id}")

    # Publicar evento
    event_bus.publish(
        "produto.estoque_atualizado",
        {
            "id": produto_id,
            "quantidade": produto.quantidade_estoque,
            "operacao": estoque_data.operacao,
        },
    )

    return produto


@router.get("/categoria/{categoria}", response_model=list[ProdutoResponse])
def listar_por_categoria(categoria: str, db: Session = Depends(get_db)):
    """Lista produtos de uma categoria"""
    produtos = (
        db.query(Produto)
        .filter(Produto.categoria == categoria, Produto.ativo == 1)
        .all()
    )
    return produtos
