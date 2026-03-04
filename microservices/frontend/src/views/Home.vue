<template>
	<div>
		<h1 class="text-3xl font-bold mb-8">Dashboard</h1>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
			<div class="card bg-blue-50 border-l-4 border-blue-500">
				<h3 class="text-lg font-semibold text-gray-700 mb-2">
					Total de Produtos
				</h3>
				<p class="text-3xl font-bold text-blue-600">
					{{ stats.totalProdutos }}
				</p>
			</div>

			<div class="card bg-green-50 border-l-4 border-green-500">
				<h3 class="text-lg font-semibold text-gray-700 mb-2">Pedidos Ativos</h3>
				<p class="text-3xl font-bold text-green-600">
					{{ stats.pedidosAtivos }}
				</p>
			</div>

			<div class="card bg-purple-50 border-l-4 border-purple-500">
				<h3 class="text-lg font-semibold text-gray-700 mb-2">Valor Total</h3>
				<p class="text-3xl font-bold text-purple-600">
					R$ {{ stats.valorTotal.toFixed(2) }}
				</p>
			</div>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<div class="card">
				<h2 class="text-xl font-bold mb-4">Ações Rápidas</h2>
				<div class="space-y-2">
					<router-link
						to="/produtos/novo"
						class="btn btn-primary block text-center"
					>
						➕ Novo Produto
					</router-link>
					<router-link
						to="/pedidos/novo"
						class="btn btn-success block text-center"
					>
						🛒 Novo Pedido
					</router-link>
					<router-link
						to="/simulador"
						class="btn btn-secondary block text-center"
					>
						🧮 Simulador de Estratégias
					</router-link>
				</div>
			</div>

			<div class="card">
				<h2 class="text-xl font-bold mb-4">Últimos Pedidos</h2>
				<div v-if="ultimosPedidos.length" class="space-y-2">
					<div
						v-for="pedido in ultimosPedidos"
						:key="pedido.id"
						class="p-3 bg-gray-50 rounded-lg flex justify-between items-center"
					>
						<div>
							<p class="font-semibold">{{ pedido.numero }}</p>
							<p class="text-sm text-gray-600">{{ pedido.status }}</p>
						</div>
						<p class="font-bold text-green-600">R$ {{ pedido.valor_total }}</p>
					</div>
				</div>
				<p v-else class="text-gray-500 text-center py-4">Nenhum pedido ainda</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const stats = ref({
	totalProdutos: 0,
	pedidosAtivos: 0,
	valorTotal: 0,
});

const ultimosPedidos = ref([]);

async function loadDashboard() {
	try {
		const [produtosRes, pedidosRes] = await Promise.all([
			api.get('/produtos?per_page=100'),
			api.get('/pedidos?per_page=5'),
		]);

		stats.value.totalProdutos = produtosRes.data.total || 0;
		stats.value.pedidosAtivos = pedidosRes.data.total || 0;

		ultimosPedidos.value = pedidosRes.data.items || [];
		stats.value.valorTotal = ultimosPedidos.value.reduce(
			(sum, p) => sum + parseFloat(p.valor_total || 0),
			0,
		);
	} catch (error) {
		console.error('Erro ao carregar dashboard:', error);
	}
}

onMounted(() => {
	loadDashboard();
});
</script>
