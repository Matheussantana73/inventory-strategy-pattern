# Sistema de Estoque - Microserviços

Este projeto transforma o sistema monolítico de estoque Django em uma arquitetura de microserviços usando FastAPI, Docker e NGINX.

## Arquitetura

```
                            ┌──────────────────┐
                            │   API Gateway    │
                            │     (NGINX)      │
                            │    porta 80      │
                            └────────┬─────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   Produto     │          │    Pedido     │          │    Cálculo    │
│   Service     │◄────────►│   Service     │◄────────►│   Service     │
│  (8001)       │          │  (8002)       │          │  (8003)       │
└───────┬───────┘          └───────┬───────┘          └───────────────┘
        │                          │
        │                          │                   ┌───────────────┐
        │                          │                   │     Auth      │
        │                          │                   │   Service     │
        │                          │                   │  (8004)       │
        │                          │                   └───────┬───────┘
        │                          │                           │
        ▼                          ▼                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            PostgreSQL                                │
│                            (5432)                                    │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                            ┌────────▼────────┐
                            │      Redis      │
                            │      (6379)     │
                            └─────────────────┘
```

## Serviços

| Serviço             | Porta | Descrição                                          |
| ------------------- | ----- | -------------------------------------------------- |
| **Frontend**        | 3000  | Interface Vue.js 3 + Tailwind CSS                  |
| **API Gateway**     | 80    | NGINX - Roteamento, load balancing, rate limiting  |
| **Produto Service** | 8001  | CRUD de produtos e gerenciamento de estoque        |
| **Pedido Service**  | 8002  | CRUD de pedidos e itens                            |
| **Cálculo Service** | 8003  | Estratégias de desconto e frete (Strategy Pattern) |
| **Auth Service**    | 8004  | Autenticação JWT e gerenciamento de usuários       |
| **PostgreSQL**      | 5432  | Banco de dados relacional                          |
| **Redis**           | 6379  | Cache e message broker                             |

## 🛠️ Tecnologias

### Frontend

- **Vue 3** - Framework JavaScript progressivo
- **Vue Router** - Roteamento SPA
- **Pinia** - Gerenciamento de estado
- **Axios** - Cliente HTTP
- **Tailwind CSS** - Framework CSS utilitário
- **Vite** - Build tool e dev server

### Backend

- **FastAPI** 0.109.0 - Framework web moderno e rápido
- **SQLAlchemy** 2.0.25 - ORM Python
- **Pydantic** 2.5.3 - Validação de dados
- **PostgreSQL** 15 - Banco de dados relacional
- **Redis** 7 - Cache e message broker
- **Python-Jose** - JWT tokens
- **Passlib** - Hashing de senhas (bcrypt)

### Infraestrutura

- **Docker** & **Docker Compose** - Containerização
- **NGINX** - API Gateway e reverse proxy
- **Uvicorn** - ASGI server

## Requisitos

- Docker 20.10+
- Docker Compose 2.0+

## Como Executar

### Usando scripts

```bash
# Dar permissão de execução aos scripts
chmod +x microservices/scripts/*.sh

# Iniciar todos os serviços
./microservices/scripts/start.sh

# Parar todos os serviços
./microservices/scripts/stop.sh

# Ver logs
./microservices/scripts/logs.sh
# Ou de um serviço específico
./microservices/scripts/logs.sh produto-service
```

### Usando Docker Compose diretamente

```bash
cd microservices

# Build e execução
docker-compose up --build

# Execução em background
docker-compose up -d --build

# Parar serviços
docker-compose down

# Parar e remover volumes (reset banco)
docker-compose down -v
```

## URLs de Acesso

### 🖥️ Frontend (Interface Web)

- **URL Principal:** http://localhost:3000
- Interface Vue.js completa com todas as funcionalidades
- Login, dashboard, gerenciamento de produtos e pedidos
- Simulador de estratégias

### API Gateway

- **Base URL:** http://localhost

### Documentação Swagger

- **Produtos:** http://localhost/produtos/docs
- **Pedidos:** http://localhost/pedidos/docs
- **Cálculos:** http://localhost/calculos/docs
- **Autenticação:** http://localhost/auth/docs

### Health Checks

- http://localhost/health
- http://localhost/produtos/health
- http://localhost/pedidos/health
- http://localhost/calculos/health
- http://localhost/auth/health

## Usuário Padrão

- **Email:** admin@estoque.com
- **Senha:** admin123
- **Permissão:** Administrador

## 🚀 Usando o Frontend

A maneira mais fácil de usar o sistema é através da interface web:

1. **Acesse:** http://localhost:3000
2. **Faça login** com as credenciais acima
3. **Navegue pelas funcionalidades:**
   - 📊 **Dashboard** - Visão geral do sistema
   - 📦 **Produtos** - Gerencie o catálogo e estoque
   - 🛒 **Pedidos** - Crie e acompanhe pedidos
   - 🧮 **Simulador** - Compare estratégias de desconto e frete

### Funcionalidades do Frontend

#### Dashboard

- Estatísticas em tempo real
- Ações rápidas
- Últimos pedidos

#### Produtos

- Listagem com busca e filtros
- Criar, editar e excluir produtos
- Controle de estoque
- Categorização

#### Pedidos

- Criar pedido com múltiplos itens
- Validação de estoque automática
- Cálculo automático de desconto e frete
- Controle de status: Pendente → Confirmado → Em Separação → Enviado → Entregue
- Cancelamento com estorno de estoque

#### Simulador

- Simule diferentes combinações de estratégias
- Compare resultados lado a lado
- Identifique a melhor opção automaticamente
- Visualize economia em percentual

## Exemplos de Uso

### 1. Login e obtenção de token

```bash
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@estoque.com", "senha": "admin123"}'
```

### 2. Listar produtos

```bash
curl http://localhost/api/v1/produtos
```

### 3. Criar produto (autenticado)

```bash
curl -X POST http://localhost/api/v1/produtos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "nome": "Produto Teste",
    "preco": 99.90,
    "quantidade_estoque": 50,
    "categoria": "Teste"
  }'
```

### 4. Calcular pedido com estratégias

```bash
curl -X POST http://localhost/api/v1/calcular \
  -H "Content-Type: application/json" \
  -d '{
    "valor_produtos": 1000,
    "quantidade": 5,
    "peso_kg": 10,
    "distancia_km": 50,
    "tipo_desconto": "percentual_10",
    "tipo_frete": "por_peso"
  }'
```

### 5. Simular múltiplas estratégias

```bash
curl -X POST http://localhost/api/v1/simular \
  -H "Content-Type: application/json" \
  -d '{
    "valor_produtos": 1000,
    "quantidade": 5,
    "peso_kg": 10,
    "estrategias_desconto": ["percentual_10", "percentual_20", "fixo_100"],
    "estrategias_frete": ["fixo_30", "por_peso", "gratis"]
  }'
```

### 6. Criar pedido

```bash
curl -X POST http://localhost/api/v1/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_desconto": "percentual_10",
    "tipo_frete": "fixo_30",
    "itens": [
      {"produto_id": 1, "quantidade": 2},
      {"produto_id": 2, "quantidade": 3}
    ]
  }'
```

## Estratégias Disponíveis

### Desconto

| Tipo            | Descrição                           |
| --------------- | ----------------------------------- |
| `percentual_10` | Desconto de 10%                     |
| `percentual_15` | Desconto de 15%                     |
| `percentual_20` | Desconto de 20%                     |
| `percentual_30` | Desconto de 30%                     |
| `fixo_50`       | Desconto fixo de R$ 50              |
| `fixo_100`      | Desconto fixo de R$ 100             |
| `progressivo`   | Desconto progressivo por quantidade |
| `por_valor`     | Desconto progressivo por valor      |
| `sem_desconto`  | Sem desconto                        |

### Frete

| Tipo             | Descrição               |
| ---------------- | ----------------------- |
| `por_peso`       | R$ 5,00 por kg          |
| `por_distancia`  | R$ 2,00 por km          |
| `peso_distancia` | R$ 3,00/kg + R$ 1,50/km |
| `fixo_30`        | Frete fixo R$ 30        |
| `fixo_50`        | Frete fixo R$ 50        |
| `gratis`         | Frete grátis            |
| `condicional`    | Grátis acima de R$ 500  |

## Estrutura do Projeto

```
microservices/
├── docker-compose.yml          # Orquestração dos containers
├── ARCHITECTURE.md             # Documentação da arquitetura
├── README.md                   # Este arquivo
│
├── frontend/                   # Interface Web Vue.js
│   ├── Dockerfile
│   ├── nginx.conf              # Config NGINX do frontend
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── api/                # Cliente HTTP
│       ├── assets/
│       ├── components/         # Componentes reutilizáveis
│       ├── router/             # Vue Router
│       ├── stores/             # Pinia (estado global)
│       └── views/              # Páginas/Views
│           ├── Home.vue
│           ├── Login.vue
│           ├── Simulador.vue
│           ├── produtos/
│           └── pedidos/
│
├── shared/                     # Código compartilhado
│   ├── __init__.py
│   ├── database.py             # Configuração SQLAlchemy
│   └── redis_client.py         # Cliente Redis
│
├── produto_service/            # Serviço de Produtos
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── app/
│       ├── models.py
│       ├── schemas.py
│       └── routes.py
│
├── pedido_service/             # Serviço de Pedidos
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── app/
│       ├── models.py
│       ├── schemas.py
│       └── routes.py
│
├── calculo_service/            # Serviço de Cálculos
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── app/
│       ├── calculadora.py
│       ├── schemas.py
│       ├── routes.py
│       └── strategies/
│           ├── __init__.py
│           ├── desconto.py
│           └── frete.py
│
├── auth_service/               # Serviço de Autenticação
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── app/
│       ├── auth.py
│       ├── models.py
│       ├── schemas.py
│       └── routes.py
│
├── nginx/                      # API Gateway
│   ├── Dockerfile
│   └── nginx.conf
│
└── scripts/                    # Scripts utilitários
    ├── init-db.sql
    ├── start.sh
    ├── stop.sh
    └── logs.sh
```

## Desenvolvimento

### Adicionar novo serviço

1. Criar pasta em `microservices/novo_service/`
2. Criar `Dockerfile`, `requirements.txt`, `main.py`
3. Adicionar serviço no `docker-compose.yml`
4. Configurar rotas no `nginx/nginx.conf`

### Executar serviço individualmente (dev)

```bash
cd microservices/produto_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Licença

MIT License
