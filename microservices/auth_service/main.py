"""Serviço de Autenticação - API principal"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from shared.database import engine, Base, SessionLocal

from app.routes import router
from app.models import Usuario, TokenRevogado  # Importar para criar tabelas
from app.auth import hash_senha


def create_default_user():
    """Cria usuário admin padrão se não existir"""
    db = SessionLocal()
    try:
        # Verificar se já existe o usuário admin
        existing_user = db.query(Usuario).filter(Usuario.email == "admin@estoque.com").first()
        if not existing_user:
            admin_user = Usuario(
                email="admin@estoque.com",
                nome="Administrador",
                senha_hash=hash_senha("admin123"),
                is_admin=True,
                ativo=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Usuário admin padrão criado com sucesso!")
        else:
            print("ℹ️  Usuário admin já existe")
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle: criar tabelas ao iniciar"""
    Base.metadata.create_all(bind=engine)
    # Criar usuário padrão
    create_default_user()
    yield


app = FastAPI(
    title="Auth Service",
    description="Microserviço de autenticação e autorização com JWT",
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
    return {"status": "healthy", "service": "auth-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
