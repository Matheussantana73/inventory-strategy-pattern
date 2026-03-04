#!/bin/bash
# Script para ver logs dos serviços

cd "$(dirname "$0")/.."

if [ -z "$1" ]; then
    echo "📋 Mostrando logs de todos os serviços..."
    docker-compose logs -f
else
    echo "📋 Mostrando logs do serviço: $1"
    docker-compose logs -f "$1"
fi
