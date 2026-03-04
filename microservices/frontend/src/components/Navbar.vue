<template>
	<nav class="bg-white shadow-lg">
		<div class="container mx-auto px-4">
			<div class="flex justify-between items-center py-4">
				<div class="flex items-center space-x-8">
					<router-link to="/" class="text-xl font-bold text-blue-600">
						📦 Sistema de Estoque
					</router-link>
					<div class="hidden md:flex space-x-4">
						<router-link to="/" class="nav-link">Dashboard</router-link>
						<router-link to="/produtos" class="nav-link">Produtos</router-link>
						<router-link to="/pedidos" class="nav-link">Pedidos</router-link>
						<router-link to="/simulador" class="nav-link"
							>Simulador</router-link
						>
					</div>
				</div>

				<div class="flex items-center space-x-4">
					<span class="text-sm text-gray-600">
						Olá, {{ authStore.user?.nome || 'Usuário' }}
					</span>
					<button @click="handleLogout" class="btn btn-secondary text-sm">
						Sair
					</button>
				</div>
			</div>
		</div>
	</nav>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

async function handleLogout() {
	await authStore.logout();
	router.push('/login');
}
</script>

<style scoped>
.nav-link {
	@apply text-gray-600 hover:text-blue-600 font-medium transition-colors;
}

.router-link-active {
	@apply text-blue-600;
}
</style>
