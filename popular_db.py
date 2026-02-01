"""
Script para popular o banco de dados com produtos de exemplo
Execute com: python popular_db.py
"""

import os
import django
from estoque.models import Produto

# Configurar o Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "estoque_project.settings")
django.setup()


# Limpar produtos existentes (cuidado em produção!)
# Produto.objects.all().delete()

produtos_exemplo = [
    {
        "nome": "Notebook Dell Inspiron",
        "preco": 3500.00,
        "peso": 2.5,
        "quantidade_estoque": 10,
    },
    {
        "nome": "Mouse Logitech MX Master",
        "preco": 350.00,
        "peso": 0.2,
        "quantidade_estoque": 50,
    },
    {
        "nome": "Teclado Mecânico Keychron",
        "preco": 650.00,
        "peso": 0.8,
        "quantidade_estoque": 30,
    },
    {
        "nome": "Monitor LG 27 polegadas",
        "preco": 1200.00,
        "peso": 5.0,
        "quantidade_estoque": 15,
    },
    {
        "nome": "Webcam Logitech C920",
        "preco": 450.00,
        "peso": 0.3,
        "quantidade_estoque": 25,
    },
    {
        "nome": "Headset HyperX Cloud II",
        "preco": 550.00,
        "peso": 0.4,
        "quantidade_estoque": 40,
    },
    {
        "nome": "SSD Samsung 1TB",
        "preco": 600.00,
        "peso": 0.1,
        "quantidade_estoque": 60,
    },
    {
        "nome": "Memória RAM 16GB DDR4",
        "preco": 400.00,
        "peso": 0.05,
        "quantidade_estoque": 80,
    },
    {
        "nome": "Hub USB-C 7 portas",
        "preco": 250.00,
        "peso": 0.2,
        "quantidade_estoque": 35,
    },
    {
        "nome": "Mousepad Gamer Grande",
        "preco": 80.00,
        "peso": 0.5,
        "quantidade_estoque": 100,
    },
]

print("🏪 Populando banco de dados com produtos de exemplo...\n")

for produto_data in produtos_exemplo:
    produto, criado = Produto.objects.get_or_create(
        nome=produto_data["nome"],
        defaults={
            "preco": produto_data["preco"],
            "peso": produto_data["peso"],
            "quantidade_estoque": produto_data["quantidade_estoque"],
        },
    )

    if criado:
        print(
            f"✅ Criado: {produto.nome} - R$ {produto.preco} ({produto.quantidade_estoque} em estoque)"
        )
    else:
        print(f"ℹ️  Já existe: {produto.nome}")

print(f"\n🎉 Processo concluído! Total de produtos: {Produto.objects.count()}")
