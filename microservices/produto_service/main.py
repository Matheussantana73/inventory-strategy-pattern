"""Serviço de Produtos - API principal"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from shared.database import engine, Base

from app.routes import router
from app.models import Produto  # Importar para criar tabelas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle: criar tabelas ao iniciar"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Produto Service",
    description="Microserviço de gerenciamento de produtos e estoque",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(router)


@app.get("/health")
def health_check():
    """Endpoint de health check"""
    return {"status": "healthy", "service": "produto-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
