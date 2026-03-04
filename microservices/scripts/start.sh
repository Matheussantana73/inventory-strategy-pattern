#!/bin/bash
# Script para iniciar os microserviços

set -e

echo "🚀 Iniciando microserviços do Sistema de Estoque..."
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Navegar para o diretório de microserviços
cd "$(dirname "$0")/.."

echo "📦 Construindo imagens Docker..."
docker-compose build

echo ""
echo "🐳 Iniciando containers..."
docker-compose up -d

echo ""
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Verificar health checks
echo ""
echo "🔍 Verificando status dos serviços..."

services=("db" "redis" "produto-service" "pedido-service" "calculo-service" "auth-service" "nginx")

for service in "${services[@]}"; do
    if docker-compose ps "$service" | grep -q "Up"; then
        echo "  ✅ $service está rodando"
    else
        echo "  ❌ $service não está rodando"
    fi
done

echo ""
echo "=========================================="
echo "🎉 Sistema iniciado com sucesso!"
echo "=========================================="
echo ""
echo "📍 URLs de acesso:"
echo "   • API Gateway:     http://localhost"
echo "   • Health Check:    http://localhost/health"
echo ""
echo "📚 Documentação Swagger:"
echo "   • Produtos:        http://localhost/produtos/docs"
echo "   • Pedidos:         http://localhost/pedidos/docs"
echo "   • Cálculos:        http://localhost/calculos/docs"
echo "   • Autenticação:    http://localhost/auth/docs"
echo ""
echo "🔑 Usuário admin padrão:"
echo "   • Email: admin@estoque.com"
echo "   • Senha: admin123"
echo ""
echo "📝 Comandos úteis:"
echo "   • Ver logs:        docker-compose logs -f"
echo "   • Parar serviços:  docker-compose down"
echo "   • Resetar banco:   docker-compose down -v && docker-compose up -d"
echo ""
