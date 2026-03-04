#!/bin/bash
# Script para parar os microserviços

set -e

echo "🛑 Parando microserviços do Sistema de Estoque..."
echo ""

# Navegar para o diretório de microserviços
cd "$(dirname "$0")/.."

docker-compose down

echo ""
echo "✅ Todos os serviços foram parados."
echo ""
echo "💡 Para remover também os volumes (dados), use:"
echo "   docker-compose down -v"
echo ""
