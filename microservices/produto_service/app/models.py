"""Modelos do serviço de produtos"""

from sqlalchemy import Column, Integer, String, Float, Numeric, DateTime
from sqlalchemy.sql import func
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from shared.database import Base


class Produto(Base):
    """Modelo de Produto"""

    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    descricao = Column(String(500), nullable=True)
    preco = Column(Numeric(10, 2), nullable=False)
    peso = Column(Float, default=0)
    quantidade_estoque = Column(Integer, default=0)
    categoria = Column(String(100), nullable=True, index=True)
    sku = Column(String(50), unique=True, nullable=True)
    ativo = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Produto(id={self.id}, nome='{self.nome}')>"
