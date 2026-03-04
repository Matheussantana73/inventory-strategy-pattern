# Arquitetura de Microserviços - Sistema de Estoque

## Visão Geral

O sistema monolítico foi decomposto em 5 microserviços independentes, cada um com sua própria responsabilidade.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NGINX API GATEWAY                          │
│                         (porta 80/443)                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   produto     │     │    pedido     │     │    calculo    │
│   service     │     │   service     │     │   service     │
│  (porta 8001) │     │  (porta 8002) │     │  (porta 8003) │
└───────┬───────┘     └───────┬───────┘     └───────────────┘
        │                     │
        ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PostgreSQL Database                         │
│                         (porta 5432)                                │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────┐     ┌───────────────┐
│     auth      │     │     redis     │
│   service     │     │    (cache)    │
│  (porta 8004) │     │  (porta 6379) │
└───────────────┘     └───────────────┘
```

## Microserviços

### 1. Produto Service (porta 8001)

**Responsabilidades:**

- CRUD de produtos
- Gerenciamento de estoque
- Controle de disponibilidade

**Endpoints:**

- `GET /api/v1/produtos` - Listar produtos
- `GET /api/v1/produtos/{id}` - Obter produto
- `POST /api/v1/produtos` - Criar produto
- `PUT /api/v1/produtos/{id}` - Atualizar produto
- `DELETE /api/v1/produtos/{id}` - Deletar produto
- `PUT /api/v1/produtos/{id}/estoque` - Atualizar estoque

### 2. Pedido Service (porta 8002)

**Responsabilidades:**

- CRUD de pedidos
- Gerenciamento de itens do pedido
- Histórico de pedidos

**Endpoints:**

- `GET /api/v1/pedidos` - Listar pedidos
- `GET /api/v1/pedidos/{id}` - Obter pedido
- `POST /api/v1/pedidos` - Criar pedido
- `PUT /api/v1/pedidos/{id}` - Atualizar pedido
- `DELETE /api/v1/pedidos/{id}` - Cancelar pedido
- `GET /api/v1/pedidos/{id}/itens` - Listar itens do pedido

### 3. Cálculo Service (porta 8003)

**Responsabilidades:**

- Estratégias de desconto
- Estratégias de frete
- Cálculo final do pedido

**Endpoints:**

- `POST /api/v1/calcular` - Calcular total com estratégias
- `GET /api/v1/estrategias/desconto` - Listar estratégias de desconto
- `GET /api/v1/estrategias/frete` - Listar estratégias de frete

### 4. Auth Service (porta 8004) - **NOVO**

**Responsabilidades:**

- Autenticação de usuários
- Autorização (JWT)
- Gerenciamento de permissões

**Endpoints:**

- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Registro
- `POST /api/v1/auth/refresh` - Renovar token
- `GET /api/v1/auth/me` - Dados do usuário logado
- `POST /api/v1/auth/logout` - Logout

### 5. API Gateway (NGINX)

**Responsabilidades:**

- Roteamento de requisições
- Load balancing
- Rate limiting
- SSL termination

## Tecnologias

| Componente     | Tecnologia              |
| -------------- | ----------------------- |
| API Services   | FastAPI (Python)        |
| Banco de Dados | PostgreSQL 15           |
| Cache          | Redis 7                 |
| API Gateway    | NGINX                   |
| Containers     | Docker + Docker Compose |
| Validação      | Pydantic v2             |
| ORM            | SQLAlchemy              |
| Autenticação   | JWT (python-jose)       |
| Migrações      | Alembic                 |

## Comunicação entre Serviços

- **Síncrona:** HTTP/REST via API Gateway
- **Assíncrona:** Redis Pub/Sub para eventos
- **Cache:** Redis para dados frequentes

## Portas

| Serviço         | Porta Interna | Porta Externa |
| --------------- | ------------- | ------------- |
| API Gateway     | 80            | 80            |
| Produto Service | 8001          | -             |
| Pedido Service  | 8002          | -             |
| Cálculo Service | 8003          | -             |
| Auth Service    | 8004          | -             |
| PostgreSQL      | 5432          | 5432          |
| Redis           | 6379          | 6379          |

## Como Executar

```bash
# Build e execução de todos os serviços
docker-compose up --build

# Executar em background
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

## URLs de Acesso

- **API Gateway:** http://localhost
- **Documentação Swagger:**
  - Produtos: http://localhost/produtos/docs
  - Pedidos: http://localhost/pedidos/docs
  - Cálculos: http://localhost/calculos/docs
  - Auth: http://localhost/auth/docs
