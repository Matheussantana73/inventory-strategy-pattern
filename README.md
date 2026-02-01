# Sistema de Estoque em Django

Sistema de gerenciamento de estoque implementado com Django utilizando o **padrão de projeto Strategy**.

## � Início Rápido

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Configuração e Execução

Este projeto utiliza um Makefile para facilitar a configuração e execução. Para começar:

```bash
# Configurar todo o projeto (cria venv, instala dependências, executa migrações e popula o banco)
make setup

# Iniciar o servidor de desenvolvimento
make run
```

Acesse: http://localhost:8000

### Comandos Disponíveis

```bash
make help        # Mostra todos os comandos disponíveis
make setup       # Configura todo o projeto (venv + install + migrate + populate)
make venv        # Cria o ambiente virtual
make install     # Instala as dependências
make migrate     # Executa as migrações do banco de dados
make populate    # Popula o banco com dados de exemplo
make run         # Inicia o servidor de desenvolvimento
make test        # Executa os testes
make shell       # Abre o shell do Django
make superuser   # Cria um superusuário admin
make clean       # Remove banco de dados, venv e arquivos cache
```

## �📋 Descrição

Este projeto implementa um sistema de estoque que utiliza o padrão Strategy para:

- Diferentes formas de cálculo de desconto (percentual, fixo, progressivo)
- Diferentes formas de cálculo de frete (por peso, por distância, fixo)
- Troca dinâmica de comportamento em tempo de execução

## 🎨 O Padrão Strategy Aplicado

### O que é o Padrão Strategy?

O **Strategy** é um padrão de projeto comportamental que permite definir uma família de algoritmos, encapsular cada um deles e torná-los intercambiáveis. O padrão Strategy permite que o algoritmo varie independentemente dos clientes que o utilizam.

### Problema Resolvido

Imagine um sistema de e-commerce que precisa calcular descontos e fretes de diferentes formas dependendo do tipo de cliente, promoção ou região. Sem o padrão Strategy, teríamos:

```python
# ❌ Abordagem SEM Strategy (código acoplado e difícil de manter)
def calcular_pedido(valor, tipo_cliente, regiao):
    if tipo_cliente == "VIP":
        if valor > 1000:
            desconto = valor * 0.15
        else:
            desconto = valor * 0.10
    elif tipo_cliente == "COMUM":
        desconto = 50
    else:
        desconto = 0

    if regiao == "SUL":
        frete = peso * 5
    elif regiao == "SUDESTE":
        frete = 30
    else:
        frete = 50

    return valor - desconto + frete
```

**Problemas:**

- ❌ Código rígido e difícil de testar
- ❌ Adicionar novo tipo de desconto requer modificar a função existente (viola Open/Closed Principle)
- ❌ Lógica de negócio dispersa em múltiplos if/else
- ❌ Impossível reutilizar estratégias em outros contextos
- ❌ Difícil de testar cada cenário isoladamente

### Como o Strategy Resolve

Com o padrão Strategy, separamos cada algoritmo em sua própria classe:

```python
# ✅ Abordagem COM Strategy (flexível e extensível)

# 1. Interface/Classe Base (contrato)
class EstrategiaDesconto(ABC):
    @abstractmethod
    def calcular_desconto(self, valor: float, **kwargs) -> float:
        pass

# 2. Estratégias Concretas (implementações)
class DescontoPercentual(EstrategiaDesconto):
    def __init__(self, percentual: float):
        self.percentual = percentual

    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return valor * (self.percentual / 100)

class DescontoFixo(EstrategiaDesconto):
    def __init__(self, valor_desconto: float):
        self.valor_desconto = valor_desconto

    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return min(self.valor_desconto, valor)

# 3. Contexto (utiliza as estratégias)
class CalculadoraPedido:
    def __init__(self, estrategia_desconto: EstrategiaDesconto):
        self._estrategia_desconto = estrategia_desconto

    def calcular_total(self, valor_produtos: float) -> float:
        desconto = self._estrategia_desconto.calcular_desconto(valor_produtos)
        return valor_produtos - desconto
```

### Estrutura do Padrão no Projeto

```
┌─────────────────────────────────────────────────────────────┐
│                    PADRÃO STRATEGY                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │  <<interface>>   │         │  <<interface>>   │        │
│  │ EstrategiaDesconto│        │  EstrategiaFrete │        │
│  └────────┬─────────┘         └────────┬─────────┘        │
│           │                            │                   │
│           │ implements                 │ implements        │
│  ┌────────┴─────────────┐    ┌────────┴─────────────┐    │
│  │  Estratégias         │    │  Estratégias         │    │
│  │  Concretas:          │    │  Concretas:          │    │
│  │  • DescontoPercentual│    │  • FretePorPeso      │    │
│  │  • DescontoFixo      │    │  • FretePorDistancia │    │
│  │  • DescontoProgressivo│   │  • FreteFixo         │    │
│  │  • SemDesconto       │    │  • FreteGratis       │    │
│  └──────────────────────┘    └──────────────────────┘    │
│           ▲                            ▲                   │
│           │                            │                   │
│           │ usa                        │ usa               │
│           │                            │                   │
│  ┌────────┴────────────────────────────┴─────────┐        │
│  │           CalculadoraPedido                    │        │
│  │  (Contexto - utiliza as estratégias)          │        │
│  │  + calcular_total()                            │        │
│  │  + set_estrategia_desconto()                   │        │
│  │  + set_estrategia_frete()                      │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Aplicação Prática no Projeto

#### 1. **Interface/Classe Base** (strategies/desconto.py)

Define o contrato que todas as estratégias devem seguir:

```python
class EstrategiaDesconto(ABC):
    @abstractmethod
    def calcular_desconto(self, valor: float, **kwargs) -> float:
        """Contrato: todas as estratégias devem implementar este método"""
        pass
```

#### 2. **Estratégias Concretas** (implementações específicas)

Cada estratégia encapsula um algoritmo diferente:

```python
# Desconto baseado em porcentagem
class DescontoPercentual(EstrategiaDesconto):
    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return valor * (self.percentual / 100)

# Desconto de valor fixo
class DescontoFixo(EstrategiaDesconto):
    def calcular_desconto(self, valor: float, **kwargs) -> float:
        return min(self.valor_desconto, valor)

# Desconto que aumenta conforme a quantidade
class DescontoProgressivo(EstrategiaDesconto):
    def calcular_desconto(self, valor: float, quantidade: int = 0, **kwargs) -> float:
        percentual = self._calcular_percentual_por_faixa(quantidade)
        return valor * (percentual / 100)
```

#### 3. **Contexto** (calculadora_pedido.py)

Utiliza as estratégias sem conhecer os detalhes de implementação:

```python
class CalculadoraPedido:
    def __init__(self, estrategia_desconto, estrategia_frete):
        self._estrategia_desconto = estrategia_desconto
        self._estrategia_frete = estrategia_frete

    def calcular_total(self, valor_produtos, peso_kg, distancia_km):
        # Delega o cálculo para as estratégias
        desconto = self._estrategia_desconto.calcular_desconto(valor_produtos)
        frete = self._estrategia_frete.calcular_frete(peso_kg=peso_kg)
        return valor_produtos - desconto + frete

    # ✨ Permite trocar estratégia em tempo de execução
    def set_estrategia_desconto(self, nova_estrategia):
        self._estrategia_desconto = nova_estrategia
```

### Fluxo de Execução Real

```python
# 1️⃣ Cliente VIP: Desconto progressivo + Frete grátis
desconto_vip = DescontoProgressivo({100: 5, 500: 10, 1000: 15})
frete_vip = FreteGratis()
calculadora = CalculadoraPedido(desconto_vip, frete_vip)

resultado = calculadora.calcular_total(
    valor_produtos=2000,
    quantidade=600,  # 600 unidades → 10% de desconto
    peso_kg=50
)
# Resultado: {
#   valor_produtos: 2000,
#   desconto: 200 (10%),
#   frete: 0,
#   valor_final: 1800
# }

# 2️⃣ Troca dinâmica: Cliente virou premium!
calculadora.set_estrategia_desconto(DescontoPercentual(20))  # 20% flat
resultado = calculadora.calcular_total(valor_produtos=2000)
# Agora desconto: 400 (20%), valor_final: 1600
```

### Integração com Django

#### Django Admin com Choices

```python
class Pedido(models.Model):
    class TipoDesconto(models.TextChoices):
        PERCENTUAL_10 = "percentual_10", "Desconto de 10%"
        FIXO_50 = "fixo_50", "Desconto fixo de R$ 50"
        PROGRESSIVO = "progressivo", "Desconto progressivo"
        # ...

    tipo_desconto = models.CharField(
        choices=TipoDesconto.choices,
        default=TipoDesconto.SEM_DESCONTO
    )
```

#### Views Dinâmicas

```python
def calcular_pedido_dinamico(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Factory pattern: cria estratégia baseada no tipo armazenado
    ESTRATEGIAS_DESCONTO = {
        "percentual_10": lambda: DescontoPercentual(10),
        "fixo_50": lambda: DescontoFixo(50),
        "progressivo": lambda: DescontoProgressivo({100: 5, 500: 10})
    }

    estrategia = ESTRATEGIAS_DESCONTO[pedido.tipo_desconto]()
    calculadora = CalculadoraPedido(estrategia, frete)
    resultado = calculadora.calcular_total(...)

    return JsonResponse(resultado.model_dump())
```

### Benefícios Conquistados

✅ **Open/Closed Principle**: Aberto para extensão, fechado para modificação

- Adicionar nova estratégia = criar nova classe
- Não precisa modificar código existente

✅ **Single Responsibility**: Cada classe tem uma única responsabilidade

- `DescontoPercentual`: apenas desconto percentual
- `FretePorPeso`: apenas frete por peso

✅ **Testabilidade**: Testar cada estratégia isoladamente

```python
def test_desconto_percentual():
    desconto = DescontoPercentual(10)
    assert desconto.calcular_desconto(1000) == 100
```

✅ **Flexibilidade**: Troca dinâmica em tempo de execução

```python
calculadora.set_estrategia_desconto(DescontoFixo(50))
```

✅ **Reutilização**: Mesma estratégia em contextos diferentes

```python
# Usar em pedidos
pedido_calculadora = CalculadoraPedido(DescontoPercentual(10), frete)

# Usar em orçamentos
orcamento_calculadora = CalculadoraOrcamento(DescontoPercentual(10))
```

### Quando Usar o Padrão Strategy?

✅ **Use quando:**

- Você tem múltiplas variações de um algoritmo
- Quer evitar condicionais complexos (if/else, switch)
- Algoritmos devem ser intercambiáveis em tempo de execução
- Quer isolar a lógica de negócio em classes separadas

❌ **Evite quando:**

- Você tem apenas um algoritmo
- Os algoritmos nunca mudam
- A simplicidade é mais importante que a flexibilidade

## 🏗️ Estrutura do Projeto

```
estoque_project/
├── manage.py
├── requirements.txt
├── estoque_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── estoque/
    ├── migrations/
    ├── strategies/
    │   ├── __init__.py
    │   ├── desconto.py
    │   └── frete.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── calculadora_pedido.py
    └── tests.py
```

## 🚀 Como Executar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Criar superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 4. Executar testes

```bash
python manage.py test estoque
```

### 5. Iniciar servidor

```bash
python manage.py runserver
```

## 🎯 Padrão Strategy - Componentes

### Estratégias de Desconto

- **DescontoPercentual**: Desconto baseado em percentual do valor
- **DescontoFixo**: Desconto de valor fixo
- **DescontoProgressivo**: Desconto baseado em quantidade (faixas)
- **SemDesconto**: Sem aplicação de desconto

### Estratégias de Frete

- **FretePorPeso**: Cálculo baseado no peso (R$/kg)
- **FretePorDistancia**: Cálculo baseado na distância (R$/km)
- **FreteFixo**: Valor fixo de frete
- **FreteGratis**: Frete gratuito

### Contexto

**CalculadoraPedido**: Classe que utiliza as estratégias e permite troca dinâmica em tempo de execução.

## 📝 Exemplos de Uso

### Exemplo 1: Cliente VIP

```python
from estoque.calculadora_pedido import CalculadoraPedido
from estoque.strategies.desconto import DescontoProgressivo
from estoque.strategies.frete import FreteGratis

desconto_vip = DescontoProgressivo({100: 5, 500: 10, 1000: 15})
frete_vip = FreteGratis()
calculadora_vip = CalculadoraPedido(desconto_vip, frete_vip)

resultado = calculadora_vip.calcular_total(
    valor_produtos=2000,
    quantidade=600,
    peso_kg=50
)
# Resultado: desconto de 200 (10%), frete 0, total 1800
```

### Exemplo 2: Cliente Comum

```python
from estoque.strategies.desconto import DescontoFixo
from estoque.strategies.frete import FretePorPeso

desconto_comum = DescontoFixo(30)
frete_comum = FretePorPeso(valor_por_kg=5)
calculadora_comum = CalculadoraPedido(desconto_comum, frete_comum)

resultado = calculadora_comum.calcular_total(
    valor_produtos=500,
    peso_kg=10
)
# Resultado: desconto de 30, frete de 50, total 520
```

### Exemplo 3: Trocar Estratégia em Tempo de Execução

```python
from estoque.strategies.desconto import DescontoPercentual

calculadora_comum.set_estrategia_desconto(DescontoPercentual(15))
resultado = calculadora_comum.calcular_total(
    valor_produtos=500,
    peso_kg=10
)
# Resultado: desconto de 75 (15%), frete de 50, total 475
```

## 🔗 Endpoints

- `GET /estoque/criar-pedido/` - Exemplo de criação de pedido com estratégias
- `GET /estoque/pedido/<id>/` - Calcular pedido com estratégias dinâmicas
- `/admin/` - Painel administrativo do Django

## 🧪 Testes

O projeto inclui testes unitários completos para:

- Estratégias de desconto
- Estratégias de frete
- Calculadora de pedidos
- Troca dinâmica de estratégias

Execute os testes com:

```bash
python manage.py test estoque
```

## ✅ Vantagens do Padrão Strategy

- **Flexibilidade**: Troca de algoritmos em tempo de execução
- **Manutenibilidade**: Cada estratégia em sua própria classe
- **Testabilidade**: Fácil testar cada estratégia isoladamente
- **Extensibilidade**: Adicionar novas estratégias sem modificar código existente
- **Reutilização**: Estratégias podem ser usadas em diferentes contextos

## 🛠️ Tecnologias

- Python 3.12+
- Django 6.0.1
- SQLite (desenvolvimento)

## 📚 Modelos

### Produto

- nome
- preco
- peso
- quantidade_estoque

### Pedido

- numero
- data_criacao
- valor_total
- tipo_desconto
- tipo_frete

### ItemPedido

- pedido (FK)
- produto (FK)
- quantidade
- preco_unitario

## 👨‍💻 Admin

O projeto inclui configuração completa do Django Admin para gerenciar:

- Produtos
- Pedidos (com itens inline)
- Itens de Pedido

Acesse em: `http://localhost:8000/admin/`

## ✅ Checklist de Implementação

- [x] Criar `estoque/strategies/desconto.py` com classes de desconto
- [x] Criar `estoque/strategies/frete.py` com classes de frete
- [x] Criar `estoque/calculadora_pedido.py` com classe contexto
- [x] Atualizar `models.py` com campos para tipos de estratégia
- [x] Implementar `views.py` com lógica de seleção de estratégias
- [x] Criar testes unitários em `tests.py`
- [x] Testar troca dinâmica de estratégias
- [x] Documentar as estratégias disponíveis
- [x] Configurar Makefile para automação
- [x] Popular banco de dados com dados de exemplo

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais, demonstrando a implementação do padrão Strategy em Django.
