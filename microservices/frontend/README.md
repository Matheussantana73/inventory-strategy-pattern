# Frontend - Sistema de Estoque

Frontend Vue.js 3 para o sistema de gerenciamento de estoque com microserviços.

## 🚀 Tecnologias

- **Vue 3** - Framework JavaScript progressivo
- **Vue Router** - Roteamento SPA
- **Pinia** - Gerenciamento de estado
- **Axios** - Cliente HTTP
- **Tailwind CSS** - Framework CSS utilitário
- **Vite** - Build tool e dev server

## 📋 Funcionalidades

### 🔐 Autenticação

- Login com JWT
- Gerenciamento de sessão
- Guards de rota

### 📦 Produtos

- Listagem com busca e filtros
- Criação e edição
- Visualização de estoque
- Categorização

### 🛒 Pedidos

- Criação de pedidos com múltiplos itens
- Visualização detalhada
- Controle de status (Pendente → Confirmado → Em Separação → Enviado → Entregue)
- Cancelamento

### 🧮 Simulador

- Comparação de estratégias de desconto e frete
- Cálculo automático da melhor opção
- Visualização de todas as combinações possíveis

## 🛠️ Desenvolvimento Local

### Pré-requisitos

- Node.js 18+
- npm ou yarn

### Instalação

```bash
cd frontend
npm install
```

### Executar em modo desenvolvimento

```bash
npm run dev
```

Acesse: http://localhost:5173

### Build para produção

```bash
npm run build
```

Os arquivos serão gerados na pasta `dist/`.

### Preview do build

```bash
npm run preview
```

## 🐳 Docker

O frontend já está integrado ao docker-compose principal:

```bash
cd ..
docker-compose up frontend
```

Acesse: http://localhost:3000

## 📁 Estrutura do Projeto

```
frontend/
├── public/              # Arquivos estáticos
├── src/
│   ├── api/            # Cliente HTTP (axios)
│   ├── assets/         # Imagens, ícones
│   ├── components/     # Componentes reutilizáveis
│   │   └── Navbar.vue
│   ├── router/         # Configuração de rotas
│   ├── stores/         # Pinia stores (estado global)
│   │   └── auth.js
│   ├── views/          # Páginas/Views
│   │   ├── Home.vue
│   │   ├── Login.vue
│   │   ├── Simulador.vue
│   │   ├── produtos/
│   │   │   ├── ProdutosList.vue
│   │   │   └── ProdutoForm.vue
│   │   └── pedidos/
│   │       ├── PedidosList.vue
│   │       ├── PedidoForm.vue
│   │       └── PedidoDetails.vue
│   ├── App.vue         # Componente raiz
│   ├── main.js         # Entry point
│   └── style.css       # Estilos globais (Tailwind)
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🔌 Integração com API

O frontend está configurado para usar proxy no desenvolvimento:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost',  // NGINX Gateway
      changeOrigin: true
    }
  }
}
```

Em produção, o NGINX do frontend faz proxy para o NGINX Gateway.

## 🎨 Componentes e Páginas

### Páginas Principais

1. **Login** (`/login`)
   - Autenticação de usuários
   - Credenciais padrão: admin@estoque.com / admin123

2. **Dashboard** (`/`)
   - Resumo de estatísticas
   - Ações rápidas
   - Últimos pedidos

3. **Produtos** (`/produtos`)
   - Lista de produtos com busca
   - Filtro por categoria
   - CRUD completo

4. **Pedidos** (`/pedidos`)
   - Lista de pedidos com filtro por status
   - Criar novo pedido
   - Visualizar detalhes e alterar status

5. **Simulador** (`/simulador`)
   - Simular combinações de estratégias
   - Comparar resultados
   - Identificar melhor opção

### Guards de Rota

```javascript
router.beforeEach((to, from, next) => {
	const authStore = useAuthStore();

	if (to.meta.requiresAuth && !authStore.isAuthenticated) {
		next('/login'); // Redireciona para login
	} else {
		next();
	}
});
```

## 🎯 Interceptors HTTP

Axios configurado com interceptors para:

1. **Request**: Adiciona token JWT automaticamente
2. **Response**: Trata erros 401 (redireciona para login)

```javascript
// Adiciona token em todas as requisições
api.interceptors.request.use((config) => {
	const token = localStorage.getItem('access_token');
	if (token) {
		config.headers.Authorization = `Bearer ${token}`;
	}
	return config;
});
```

## 🔒 Autenticação

O sistema usa JWT com refresh tokens:

- **Access Token**: 30 minutos de validade
- **Refresh Token**: 7 dias de validade
- Tokens armazenados em `localStorage`
- Renovação automática quando necessário

## 📱 Responsividade

Interface totalmente responsiva usando Tailwind CSS:

- Grid adaptativo para diferentes tamanhos de tela
- Menu mobile-friendly
- Formulários otimizados para mobile

## 🚀 Deploy

### Variáveis de Ambiente

Em produção, ajuste a URL da API:

```javascript
// src/api/index.js
const api = axios.create({
	baseURL: process.env.VITE_API_URL || '/api/v1',
});
```

### Build Otimizado

```bash
npm run build
```

O build Vite inclui:

- Tree-shaking
- Code splitting
- Minificação
- Compressão gzip

## 🎨 Customização do Tailwind

```javascript
// tailwind.config.js
theme: {
  extend: {
    // Adicione cores personalizadas
    colors: {
      primary: '#3B82F6',
    }
  }
}
```

## 📝 Convenções de Código

- Composition API (script setup)
- Nomenclatura em PascalCase para componentes
- Props tipadas quando possível
- Emits documentados

## 🐛 Debug

### Vue DevTools

Instale a extensão Vue DevTools para debug:

- Chrome: https://chrome.google.com/webstore/detail/vuejs-devtools
- Firefox: https://addons.mozilla.org/firefox/addon/vue-js-devtools/

### Logs

```javascript
// Habilitar logs detalhados em desenvolvimento
if (import.meta.env.DEV) {
	console.log('Debug info');
}
```

## 📚 Documentação Adicional

- [Vue 3 Docs](https://vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- [Pinia](https://pinia.vuejs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vite](https://vitejs.dev/)

## 🤝 Contribuindo

1. Crie uma branch para sua feature
2. Faça commit das mudanças
3. Push para a branch
4. Abra um Pull Request

## 📄 Licença

Este projeto é parte do sistema de estoque com microserviços.
