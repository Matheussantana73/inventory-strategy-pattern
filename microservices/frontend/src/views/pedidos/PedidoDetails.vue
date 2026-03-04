<template>
	<div class="max-w-4xl mx-auto">
		<div class="flex items-center gap-4 mb-6">
			<router-link to="/pedidos" class="btn btn-secondary">
				← Voltar
			</router-link>
			<h1 class="text-3xl font-bold">Detalhes do Pedido</h1>
		</div>

		<div v-if="loading" class="text-center py-8">
			<p class="text-gray-600">Carregando pedido...</p>
		</div>

		<div v-else-if="pedido" class="space-y-6">
			<!-- Informações Gerais -->
			<div class="card">
				<div class="flex justify-between items-start mb-4">
					<div>
						<h2 class="text-2xl font-bold">{{ pedido.numero }}</h2>
						<p class="text-gray-600">
							Criado em
							{{ new Date(pedido.created_at).toLocaleString('pt-BR') }}
						</p>
					</div>
					<span
						:class="getStatusClass(pedido.status)"
						class="px-4 py-2 rounded-full text-sm font-semibold"
					>
						{{ getStatusLabel(pedido.status) }}
					</span>
				</div>

				<div class="grid grid-cols-2 gap-4 mt-6">
					<div>
						<p class="text-sm text-gray-600">Tipo de Desconto</p>
						<p class="font-semibold">{{ pedido.tipo_desconto }}</p>
					</div>
					<div>
						<p class="text-sm text-gray-600">Tipo de Frete</p>
						<p class="font-semibold">{{ pedido.tipo_frete }}</p>
					</div>
				</div>

				<div v-if="pedido.endereco_entrega" class="mt-4">
					<p class="text-sm text-gray-600">Endereço de Entrega</p>
					<p class="font-semibold">{{ pedido.endereco_entrega }}</p>
				</div>
			</div>

			<!-- Itens do Pedido -->
			<div class="card">
				<h2 class="text-xl font-bold mb-4">Itens</h2>
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead class="bg-gray-50">
							<tr>
								<th class="px-4 py-2 text-left">Produto</th>
								<th class="px-4 py-2 text-right">Preço</th>
								<th class="px-4 py-2 text-center">Qtd</th>
								<th class="px-4 py-2 text-right">Subtotal</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="item in pedido.itens" :key="item.id" class="border-t">
								<td class="px-4 py-3">{{ item.nome_produto }}</td>
								<td class="px-4 py-3 text-right">
									R$ {{ parseFloat(item.preco_unitario).toFixed(2) }}
								</td>
								<td class="px-4 py-3 text-center">{{ item.quantidade }}</td>
								<td class="px-4 py-3 text-right font-semibold">
									R$ {{ parseFloat(item.subtotal).toFixed(2) }}
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Resumo Financeiro -->
			<div class="card bg-green-50">
				<h2 class="text-xl font-bold mb-4">Resumo Financeiro</h2>
				<div class="space-y-2">
					<div class="flex justify-between text-lg">
						<span>Valor dos produtos:</span>
						<span class="font-semibold"
							>R$ {{ parseFloat(pedido.valor_produtos).toFixed(2) }}</span
						>
					</div>
					<div class="flex justify-between text-lg text-green-600">
						<span>Desconto:</span>
						<span class="font-semibold"
							>- R$ {{ parseFloat(pedido.valor_desconto).toFixed(2) }}</span
						>
					</div>
					<div class="flex justify-between text-lg">
						<span>Frete:</span>
						<span class="font-semibold"
							>R$ {{ parseFloat(pedido.valor_frete).toFixed(2) }}</span
						>
					</div>
					<hr class="my-2 border-gray-300" />
					<div class="flex justify-between text-2xl font-bold">
						<span>Total:</span>
						<span class="text-green-600"
							>R$ {{ parseFloat(pedido.valor_total).toFixed(2) }}</span
						>
					</div>
				</div>
			</div>

			<!-- Ações -->
			<div
				v-if="pedido.status !== 'cancelado' && pedido.status !== 'entregue'"
				class="card"
			>
				<h2 class="text-xl font-bold mb-4">Ações</h2>
				<div class="flex gap-4">
					<button
						v-if="pedido.status === 'pendente'"
						@click="atualizarStatus('confirmado')"
						class="btn btn-success flex-1"
					>
						✅ Confirmar Pedido
					</button>
					<button
						v-if="pedido.status === 'confirmado'"
						@click="atualizarStatus('em_separacao')"
						class="btn btn-primary flex-1"
					>
						📦 Iniciar Separação
					</button>
					<button
						v-if="pedido.status === 'em_separacao'"
						@click="atualizarStatus('enviado')"
						class="btn btn-primary flex-1"
					>
						🚚 Marcar como Enviado
					</button>
					<button
						v-if="pedido.status === 'enviado'"
						@click="atualizarStatus('entregue')"
						class="btn btn-success flex-1"
					>
						✅ Marcar como Entregue
					</button>
					<button @click="cancelarPedido" class="btn btn-danger flex-1">
						❌ Cancelar Pedido
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../../api';

const route = useRoute();
const router = useRouter();
const pedido = ref(null);
const loading = ref(false);

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

async function loadPedido() {
	loading.value = true;
	try {
		const response = await api.get(`/pedidos/${route.params.id}`);
		pedido.value = response.data;
	} catch (error) {
		console.error('Erro ao carregar pedido:', error);
		alert('Erro ao carregar pedido');
		router.push('/pedidos');
	} finally {
		loading.value = false;
	}
}

async function atualizarStatus(novoStatus) {
	try {
		await api.put(`/pedidos/${route.params.id}`, { status: novoStatus });
		await loadPedido();
	} catch (error) {
		console.error('Erro ao atualizar status:', error);
		alert('Erro ao atualizar status do pedido');
	}
}

async function cancelarPedido() {
	if (!confirm('Tem certeza que deseja cancelar este pedido?')) return;

	try {
		await api.delete(`/pedidos/${route.params.id}`);
		router.push('/pedidos');
	} catch (error) {
		console.error('Erro ao cancelar pedido:', error);
		alert('Erro ao cancelar pedido');
	}
}

onMounted(() => {
	loadPedido();
});
</script>
