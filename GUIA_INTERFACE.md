# 🏪 Sistema de Estoque com Padrão Strategy

Sistema de gerenciamento de estoque implementado em Django que demonstra o uso do **Padrão de Projeto Strategy** para cálculo de descontos e fretes em pedidos.

## 🎯 Padrão Strategy Implementado

O padrão Strategy permite definir uma família de algoritmos, encapsular cada um deles e torná-los intercambiáveis. Neste projeto, aplicamos o padrão em:

### 💰 Estratégias de Desconto

- **Desconto Percentual**: 10%, 15% ou 20% sobre o valor total
- **Desconto Fixo**: R$ 50 ou R$ 100 de desconto
- **Desconto Progressivo**: Baseado na quantidade de itens
  - ≥100 itens: 5% de desconto
  - ≥500 itens: 10% de desconto
  - ≥1000 itens: 15% de desconto
- **Sem Desconto**: Nenhum desconto aplicado

### 🚚 Estratégias de Frete

- **Frete por Peso**: R$ 5,00 por kg
- **Frete por Distância**: R$ 2,00 por km
- **Frete Fixo**: R$ 30 ou R$ 50
- **Frete Grátis**: Sem custo de frete

## 🚀 Como Executar

### 1. Configurar o Ambiente

```bash
# Instalar dependências
pip install -r requirements.txt

# Aplicar migrações
python manage.py migrate
```

### 2. Popular o Banco de Dados

```bash
# Criar produtos de exemplo
python manage.py shell < popular_db.py
```

### 3. Iniciar o Servidor

```bash
python manage.py runserver
```

### 4. Acessar o Sistema

Abra seu navegador e acesse:

- **Página Inicial**: http://localhost:8000/
- **Sistema**: http://localhost:8000/estoque/

## 🖥️ Funcionalidades das Telas Interativas

### 🏠 Página Inicial

- Visão geral do sistema
- Explicação do padrão Strategy
- Menu de navegação para todas as funcionalidades

### 🧪 Testar Estratégias

**URL**: `/estoque/testar/`

Simule diferentes combinações de estratégias em tempo real:

- Insira valor dos produtos, quantidade, peso e distância
- Selecione estratégias de desconto e frete
- Veja o cálculo detalhado instantaneamente
- Compare diferentes estratégias

**Recursos**:

- Cálculo em tempo real via AJAX
- Interface intuitiva com campos auto-explicativos
- Resultados detalhados com breakdown de valores
- Badges visuais das estratégias aplicadas

### 📦 Criar Pedido

**URL**: `/estoque/criar/`

Crie pedidos reais no sistema:

- Adicione múltiplos produtos ao pedido
- Selecione estratégias de desconto e frete
- Controle de estoque automático
- Cálculo automático de subtotais e totais

**Recursos**:

- Adicionar/remover produtos dinamicamente
- Validação de estoque em tempo real
- Cálculo automático de peso e quantidade
- Resumo do pedido antes de confirmar

### 📋 Listar Pedidos

**URL**: `/estoque/pedidos/`

Visualize todos os pedidos cadastrados:

- Lista completa com estratégias aplicadas
- Filtros e ordenação
- Acesso rápido aos detalhes

### 👁️ Detalhes do Pedido

**URL**: `/estoque/pedidos/<id>/`

Veja informações completas de um pedido:

- Itens do pedido com quantidades e preços
- Estratégias aplicadas
- Cálculo detalhado (produtos, desconto, frete, total)
- Informações de economia

## 📁 Estrutura do Projeto

```
InventoryWithStrategy/
├── estoque/
│   ├── strategies/          # Padrão Strategy
│   │   ├── desconto.py     # Estratégias de desconto
│   │   └── frete.py        # Estratégias de frete
│   ├── templates/
│   │   └── estoque/        # Templates HTML
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── testar_estrategias.html
│   │       ├── criar_pedido.html
│   │       ├── listar_pedidos.html
│   │       └── detalhes_pedido.html
│   ├── models.py           # Modelos do banco
│   ├── views.py            # Views e lógica
│   ├── urls.py             # Rotas
│   ├── calculadora_pedido.py  # Contexto do Strategy
│   └── schemas.py          # Schemas Pydantic
├── popular_db.py           # Script para popular DB
└── manage.py
```

## 🎨 Interface

O sistema possui uma interface moderna e intuitiva com:

- Design responsivo
- Gradientes coloridos
- Feedback visual imediato
- Ícones intuitivos
- Badges para estratégias
- Cards organizados
- Formulários validados

## 🧪 Testando o Padrão Strategy

### Exemplo 1: Comparar Descontos

1. Acesse "Testar Estratégias"
2. Configure: R$ 1000 em produtos, 5 itens, 10kg
3. Teste com "Desconto de 10%" → Economia de R$ 100
4. Teste com "Desconto Fixo R$ 50" → Economia de R$ 50
5. Observe como a estratégia afeta o resultado

### Exemplo 2: Desconto Progressivo

1. Configure 150 itens (≥100)
2. Selecione "Desconto Progressivo"
3. Observe desconto de 5%
4. Altere para 600 itens (≥500)
5. Desconto aumenta para 10%

### Exemplo 3: Criar Pedido Real

1. Acesse "Criar Pedido"
2. Adicione produtos (ex: Notebook + Mouse)
3. Selecione estratégias
4. Veja o resumo com peso e valores
5. Crie o pedido
6. Acesse os detalhes para ver o cálculo completo

## 💡 Benefícios do Padrão Strategy

1. **Flexibilidade**: Troque algoritmos em tempo de execução
2. **Extensibilidade**: Adicione novas estratégias sem modificar código existente
3. **Testabilidade**: Teste cada estratégia isoladamente
4. **Manutenibilidade**: Código organizado e modular
5. **Reutilização**: Estratégias podem ser reutilizadas em diferentes contextos

## 🔧 Adicionando Novas Estratégias

### Nova Estratégia de Desconto:

```python
# estoque/strategies/desconto.py
class DescontoNatal(EstrategiaDesconto):
    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return valor * 0.25  # 25% de desconto
```

### Registrar no Sistema:

```python
# estoque/views.py
ESTRATEGIAS_DESCONTO = {
    # ... estratégias existentes
    "natal": lambda: DescontoNatal(),
}
```

### Adicionar ao Model:

```python
# estoque/models.py
class TipoDesconto(models.TextChoices):
    # ... tipos existentes
    NATAL = "natal", "Desconto de Natal (25%)"
```

## 🐛 Testando APIs

### Calcular com Estratégias (GET):

```bash
curl "http://localhost:8000/estoque/api/calcular/?valor_produtos=1000&quantidade=5&peso_kg=10&distancia_km=50&tipo_desconto=percentual_10&tipo_frete=por_peso"
```

## 📚 Tecnologias Utilizadas

- **Django 5.0+**: Framework web
- **Python 3.12+**: Linguagem
- **SQLite**: Banco de dados
- **Pydantic**: Validação de dados
- **HTML/CSS/JavaScript**: Interface
- **AJAX**: Requisições assíncronas

## 🎓 Conceitos Demonstrados

- ✅ Padrão Strategy (GoF)
- ✅ Interface/Abstração (ABC)
- ✅ Polimorfismo
- ✅ Injeção de Dependência
- ✅ Single Responsibility Principle
- ✅ Open/Closed Principle
- ✅ Separação de Concerns
- ✅ MVC Pattern

## 📖 Documentação Adicional

Para mais detalhes sobre a implementação, consulte:

- [Sistema_de_Estoque_em_Django.md](Sistema_de_Estoque_em_Django.md) - Documentação técnica completa

## 🤝 Contribuindo

Este é um projeto educacional demonstrando o padrão Strategy. Sinta-se livre para:

- Adicionar novas estratégias
- Melhorar a interface
- Adicionar testes unitários
- Implementar novos recursos

## 📄 Licença

Projeto educacional - IFPI - Engenharia de Software

---

**Desenvolvido com ❤️ para demonstrar o Padrão Strategy em Django**
