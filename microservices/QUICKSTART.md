# 🚀 Início Rápido - Sistema de Estoque

## Pré-requisitos

- Docker e Docker Compose instalados

## 1️⃣ Iniciar o Sistema

```bash
cd microservices
docker-compose up --build
```

Aguarde alguns minutos para que todos os serviços inicializem...

## 2️⃣ Acessar a Interface Web

Abra seu navegador em: **http://localhost:3000**

## 3️⃣ Fazer Login

Use as credenciais padrão:

- **Email:** admin@estoque.com
- **Senha:** admin123

## 4️⃣ Explorar as Funcionalidades

### Dashboard

- Visualize estatísticas gerais
- Acesse ações rápidas

### Produtos

- Clique em "Produtos" no menu
- Adicione novos produtos clicando em "➕ Novo Produto"
- Busque e filtre produtos existentes
- Edite ou exclua produtos conforme necessário

### Pedidos

- Clique em "Pedidos" no menu
- Crie um novo pedido clicando em "🛒 Novo Pedido"
- Selecione produtos e quantidades
- Escolha estratégias de desconto e frete
- Visualize o cálculo automático

### Simulador

- Clique em "Simulador" no menu
- Configure os parâmetros (valor, peso, distância)
- Selecione múltiplas estratégias de desconto e frete
- Clique em "🚀 Simular" para comparar todas as combinações
- Veja qual é a melhor opção automaticamente

## 📊 Documentação da API

Se preferir usar a API diretamente:

- **Produtos:** http://localhost/produtos/docs
- **Pedidos:** http://localhost/pedidos/docs
- **Cálculos:** http://localhost/calculos/docs
- **Autenticação:** http://localhost/auth/docs

## 🛑 Parar o Sistema

```bash
# Ctrl+C no terminal onde está rodando
# Ou em outro terminal:
docker-compose down
```

## 🔄 Reiniciar do Zero

```bash
# Para e remove todos os dados
docker-compose down -v

# Inicia novamente
docker-compose up --build
```

## 📝 Dicas

1. **Estoque Automático**: Ao cancelar um pedido, o estoque é automaticamente restituído
2. **Validação**: O sistema valida disponibilidade de estoque antes de criar pedidos
3. **Cache**: Produtos são cacheados para melhor performance
4. **Eventos**: Operações críticas publicam eventos no Redis para auditoria

## 🐛 Problemas Comuns

### Porta já em uso

Se as portas 80 ou 3000 já estiverem em uso, edite o `docker-compose.yml`:

```yaml
frontend:
  ports:
    - '3001:80' # Mude 3000 para outra porta

nginx:
  ports:
    - '8080:80' # Mude 80 para outra porta
```

### Serviços não inicializam

Verifique se há serviços com problemas:

```bash
docker-compose ps
docker-compose logs nome-do-servico
```

### Reset completo

```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## 📚 Mais Informações

- Veja [README.md](README.md) para documentação completa
- Veja [ARCHITECTURE.md](ARCHITECTURE.md) para detalhes da arquitetura
- Veja [frontend/README.md](frontend/README.md) para desenvolver o frontend

## 🎯 Próximos Passos

Depois de explorar o sistema, você pode:

1. Adicionar mais produtos no catálogo
2. Criar pedidos com diferentes estratégias
3. Usar o simulador para encontrar as melhores combinações
4. Explorar a API através do Swagger
5. Integrar com outros sistemas usando a API REST

Divirta-se! 🎉
