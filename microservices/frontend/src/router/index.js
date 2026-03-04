import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
	history: createWebHistory(),
	routes: [
		{
			path: '/',
			name: 'home',
			component: () => import('../views/Home.vue'),
			meta: { requiresAuth: true },
		},
		{
			path: '/login',
			name: 'login',
			component: () => import('../views/Login.vue'),
			meta: { guest: true },
		},
		{
			path: '/produtos',
			name: 'produtos',
			component: () => import('../views/produtos/ProdutosList.vue'),
			meta: { requiresAuth: true },
		},
		{
			path: '/produtos/novo',
			name: 'produto-create',
			component: () => import('../views/produtos/ProdutoForm.vue'),
			meta: { requiresAuth: true },
		},
		{
			path: '/produtos/:id/editar',
			name: 'produto-edit',
			component: () => import('../views/produtos/ProdutoForm.vue'),
			meta: { requiresAuth: true },
		},
		{
			path: '/pedidos',
			name: 'pedidos',
			component: () => import('../views/pedidos/PedidosList.vue'),
			meta: { requiresAuth: true },
		},
		{
			path: '/pedidos/novo',
			name: 'pedido-create',
			component: () => import('../views/pedidos/PedidoForm.vue'),
			meta: { requiresAuth: true },
		},
		{
			path: '/pedidos/:id',
			name: 'pedido-details',
			component: () => import('../views/pedidos/PedidoDetails.vue'),
			meta: { requiresAuth: true },
		},
		{
			path: '/simulador',
			name: 'simulador',
			component: () => import('../views/Simulador.vue'),
			meta: { requiresAuth: true },
		},
	],
});

router.beforeEach((to, from, next) => {
	const authStore = useAuthStore();

	if (to.meta.requiresAuth && !authStore.isAuthenticated) {
		next('/login');
	} else if (to.meta.guest && authStore.isAuthenticated) {
		next('/');
	} else {
		next();
	}
});

export default router;
