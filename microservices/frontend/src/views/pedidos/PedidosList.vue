<template>
	<div>
		<div class="flex justify-between items-center mb-6">
			<h1 class="text-3xl font-bold">Pedidos</h1>
			<router-link to="/pedidos/novo" class="btn btn-success">
				🛒 Novo Pedido
			</router-link>
		</div>

		<div class="card mb-6">
			<select v-model="statusFilter" class="input" @change="loadPedidos">
				<option value="">Todos os status</option>
				<option value="pendente">Pendente</option>
				<option value="confirmado">Confirmado</option>
				<option value="em_separacao">Em Separação</option>
				<option value="enviado">Enviado</option>
				<option value="entregue">Entregue</option>
				<option value="cancelado">Cancelado</option>
			</select>
		</div>

		<div v-if="loading" class="text-center py-8">
			<p class="text-gray-600">Carregando pedidos...</p>
		</div>

		<div v-else-if="pedidos.length" class="space-y-4">
			<div
				v-for="pedido in pedidos"
				:key="pedido.id"
				class="card hover:shadow-lg transition-shadow cursor-pointer"
				@click="router.push(`/pedidos/${pedido.id}`)"
			>
				<div class="flex justify-between items-start">
					<div>
						<h3 class="text-xl font-bold mb-2">{{ pedido.numero }}</h3>
						<p class="text-sm text-gray-600">
							{{ new Date(pedido.created_at).toLocaleDateString('pt-BR') }}
						</p>
					</div>
					<div class="text-right">
						<span
							:class="getStatusClass(pedido.status)"
							class="px-3 py-1 rounded-full text-sm font-semibold"
						>
							{{ getStatusLabel(pedido.status) }}
						</span>
						<p class="text-2xl font-bold text-green-600 mt-2">
							R$ {{ parseFloat(pedido.valor_total).toFixed(2) }}
						</p>
					</div>
				</div>
			</div>
		</div>

		<p v-else class="text-center text-gray-500 py-8">
			Nenhum pedido encontrado
		</p>

		<div v-if="totalPages > 1" class="flex justify-center gap-2 mt-8">
			<button
				v-for="page in totalPages"
				:key="page"
				@click="
					currentPage = page;
					loadPedidos();
				"
				:class="page === currentPage ? 'btn-primary' : 'btn-secondary'"
				class="btn"
			>
				{{ page }}
			</button>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../api';

const router = useRouter();
const pedidos = ref([]);
const loading = ref(false);
const statusFilter = ref('');
const currentPage = ref(1);
const totalPages = ref(1);

function getStatusLabel(status) {
	const labels = {
		pendente: 'Pendente',
		confirmado: 'Confirmado',
		em_separacao: 'Em Separação',
		enviado: 'Enviado',
		entregue: 'Entregue',
		cancelado: 'Cancelado',
	};
	return labels[status] || status;
}

function getStatusClass(status) {
	const classes = {
		pendente: 'bg-yellow-100 text-yellow-800',
		confirmado: 'bg-blue-100 text-blue-800',
		em_separacao: 'bg-purple-100 text-purple-800',
		enviado: 'bg-indigo-100 text-indigo-800',
		entregue: 'bg-green-100 text-green-800',
		cancelado: 'bg-red-100 text-red-800',
	};
	return classes[status] || 'bg-gray-100 text-gray-800';
}

async function loadPedidos() {
	loading.value = true;
	try {
		const params = {
			page: currentPage.value,
			per_page: 10,
		};

		if (statusFilter.value) params.status = statusFilter.value;

		const response = await api.get('/pedidos', { params });
		pedidos.value = response.data.items;
		totalPages.value = response.data.pages;
	} catch (error) {
		console.error('Erro ao carregar pedidos:', error);
		alert('Erro ao carregar pedidos');
	} finally {
		loading.value = false;
	}
}

onMounted(() => {
	loadPedidos();
});
</script>
