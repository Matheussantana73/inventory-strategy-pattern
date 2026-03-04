"""Modelos do serviço de pedidos"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Numeric,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from shared.database import Base


class StatusPedido(str, enum.Enum):
    """Status possíveis do pedido"""

    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    EM_SEPARACAO = "em_separacao"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class TipoDesconto(str, enum.Enum):
    """Tipos de desconto disponíveis"""

    PERCENTUAL_10 = "percentual_10"
    PERCENTUAL_15 = "percentual_15"
    PERCENTUAL_20 = "percentual_20"
    PERCENTUAL_30 = "percentual_30"
    FIXO_50 = "fixo_50"
    FIXO_100 = "fixo_100"
    PROGRESSIVO = "progressivo"
    SEM_DESCONTO = "sem_desconto"


class TipoFrete(str, enum.Enum):
    """Tipos de frete disponíveis"""

    POR_PESO = "por_peso"
    POR_DISTANCIA = "por_distancia"
    FIXO_30 = "fixo_30"
    FIXO_50 = "fixo_50"
    GRATIS = "gratis"


class Pedido(Base):
    """Modelo de Pedido"""

    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, nullable=False, index=True)
    usuario_id = Column(Integer, nullable=True, index=True)

    status = Column(String(30), default=StatusPedido.PENDENTE.value)
    tipo_desconto = Column(String(30), default=TipoDesconto.SEM_DESCONTO.value)
    tipo_frete = Column(String(30), default=TipoFrete.FIXO_50.value)

    valor_produtos = Column(Numeric(10, 2), default=0)
    valor_desconto = Column(Numeric(10, 2), default=0)
    valor_frete = Column(Numeric(10, 2), default=0)
    valor_total = Column(Numeric(10, 2), default=0)

    peso_total = Column(Float, default=0)
    distancia_km = Column(Float, default=0)

    endereco_entrega = Column(String(500), nullable=True)
    observacoes = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    itens = relationship(
        "ItemPedido", back_populates="pedido", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Pedido(id={self.id}, numero='{self.numero}')>"


class ItemPedido(Base):
    """Modelo de Item do Pedido"""

    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(
        Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False
    )
    produto_id = Column(Integer, nullable=False, index=True)

    nome_produto = Column(String(200), nullable=False)  # Snapshot do nome
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    quantidade = Column(Integer, nullable=False)
    peso_unitario = Column(Float, default=0)
    subtotal = Column(Numeric(10, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="itens")

    def __repr__(self):
        return f"<ItemPedido(produto='{self.nome_produto}', qtd={self.quantidade})>"
