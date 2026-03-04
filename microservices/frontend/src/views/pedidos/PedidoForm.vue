<template>
	<div class="max-w-3xl mx-auto">
		<h1 class="text-3xl font-bold mb-6">Novo Pedido</h1>

		<form @submit.prevent="handleSubmit" class="space-y-6">
			<!-- Estratégias -->
			<div class="card">
				<h2 class="text-xl font-bold mb-4">Estratégias</h2>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label class="label">Tipo de Desconto</label>
						<select v-model="form.tipo_desconto" class="input">
							<option value="sem_desconto">Sem desconto</option>
							<option value="percentual_10">Desconto de 10%</option>
							<option value="percentual_15">Desconto de 15%</option>
							<option value="percentual_20">Desconto de 20%</option>
							<option value="fixo_50">Desconto fixo de R$ 50</option>
							<option value="fixo_100">Desconto fixo de R$ 100</option>
							<option value="progressivo">Desconto progressivo</option>
						</select>
					</div>

					<div>
						<label class="label">Tipo de Frete</label>
						<select v-model="form.tipo_frete" class="input">
							<option value="fixo_50">Frete fixo R$ 50</option>
							<option value="fixo_30">Frete fixo R$ 30</option>
							<option value="por_peso">Frete por peso</option>
							<option value="por_distancia">Frete por distância</option>
							<option value="gratis">Frete grátis</option>
						</select>
					</div>
				</div>

				<div class="mt-4">
					<label class="label">Distância (km)</label>
					<input
						v-model.number="form.distancia_km"
						type="number"
						step="0.1"
						class="input"
					/>
				</div>
			</div>

			<!-- Itens do Pedido -->
			<div class="card">
				<h2 class="text-xl font-bold mb-4">Itens do Pedido</h2>

				<div
					v-for="(item, index) in form.itens"
					:key="index"
					class="mb-4 p-4 bg-gray-50 rounded-lg"
				>
					<div class="flex gap-4">
						<div class="flex-1">
							<label class="label">Produto</label>
							<select
								v-model="item.produto_id"
								class="input"
								@change="updateProduto(index)"
								required
							>
								<option value="">Selecione um produto</option>
								<option
									v-for="produto in produtos"
									:key="produto.id"
									:value="produto.id"
								>
									{{ produto.nome }} - R$
									{{ parseFloat(produto.preco).toFixed(2) }}
								</option>
							</select>
						</div>

						<div class="w-32">
							<label class="label">Quantidade</label>
							<input
								v-model.number="item.quantidade"
								type="number"
								min="1"
								class="input"
								required
							/>
						</div>

						<div class="flex items-end">
							<button
								type="button"
								@click="removeItem(index)"
								class="btn btn-danger"
							>
								🗑️
							</button>
						</div>
					</div>

					<p v-if="item.produto_id" class="mt-2 text-sm text-gray-600">
						Subtotal: R$ {{ calcularSubtotal(item).toFixed(2) }}
					</p>
				</div>

				<button type="button" @click="addItem" class="btn btn-secondary w-full">
					➕ Adicionar Item
				</button>
			</div>

			<!-- Endereço -->
			<div class="card">
				<h2 class="text-xl font-bold mb-4">Informações de Entrega</h2>

				<div class="space-y-4">
					<div>
						<label class="label">Endereço de Entrega</label>
						<textarea
							v-model="form.endereco_entrega"
							class="input"
							rows="2"
						></textarea>
					</div>

					<div>
						<label class="label">Observações</label>
						<textarea
							v-model="form.observacoes"
							class="input"
							rows="2"
						></textarea>
					</div>
				</div>
			</div>

			<!-- Resumo -->
			<div v-if="form.itens.length > 0" class="card bg-blue-50">
				<h2 class="text-xl font-bold mb-4">Resumo do Pedido</h2>
				<div class="space-y-2">
					<div class="flex justify-between">
						<span>Valor dos produtos:</span>
						<span class="font-semibold"
							>R$ {{ calcularValorProdutos().toFixed(2) }}</span
						>
					</div>
					<p class="text-sm text-gray-600 italic">
						* Desconto e frete serão calculados ao criar o pedido
					</p>
				</div>
			</div>

			<div v-if="error" class="p-3 bg-red-100 text-red-700 rounded-lg">
				{{ error }}
			</div>

			<div class="flex gap-4">
				<button
					type="submit"
					:disabled="loading || form.itens.length === 0"
					class="btn btn-success flex-1"
				>
					{{ loading ? 'Criando...' : 'Criar Pedido' }}
				</button>
				<router-link to="/pedidos" class="btn btn-secondary flex-1 text-center">
					Cancelar
				</router-link>
			</div>
		</form>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../api';

const router = useRouter();
const produtos = ref([]);
const loading = ref(false);
const error = ref('');

const form = ref({
	tipo_desconto: 'sem_desconto',
	tipo_frete: 'fixo_50',
	distancia_km: 0,
	endereco_entrega: '',
	observacoes: '',
	itens: [],
});

async function loadProdutos() {
	try {
		const response = await api.get(
			'/produtos?per_page=100&apenas_disponiveis=true',
		);
		produtos.value = response.data.items;
	} catch (err) {
		console.error('Erro ao carregar produtos:', err);
	}
}

function addItem() {
	form.value.itens.push({
		produto_id: '',
		quantidade: 1,
	});
}

function removeItem(index) {
	form.value.itens.splice(index, 1);
}

function updateProduto(index) {
	// Força recálculo do subtotal
	form.value.itens[index].quantidade = form.value.itens[index].quantidade || 1;
}

function calcularSubtotal(item) {
	if (!item.produto_id) return 0;
	const produto = produtos.value.find((p) => p.id === item.produto_id);
	return produto ? parseFloat(produto.preco) * item.quantidade : 0;
}

function calcularValorProdutos() {
	return form.value.itens.reduce(
		(sum, item) => sum + calcularSubtotal(item),
		0,
	);
}

async function handleSubmit() {
	if (form.value.itens.length === 0) {
		error.value = 'Adicione pelo menos um item ao pedido';
		return;
	}

	loading.value = true;
	error.value = '';

	try {
		const response = await api.post('/pedidos', form.value);
		router.push(`/pedidos/${response.data.id}`);
	} catch (err) {
		console.error('Erro ao criar pedido:', err);
		error.value = err.response?.data?.detail || 'Erro ao criar pedido';
	} finally {
		loading.value = false;
	}
}

onMounted(() => {
	loadProdutos();
	addItem(); // Adiciona primeiro item
});
</script>
