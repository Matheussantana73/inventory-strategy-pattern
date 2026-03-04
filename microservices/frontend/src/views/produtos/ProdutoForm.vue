<template>
	<div class="max-w-2xl mx-auto">
		<h1 class="text-3xl font-bold mb-6">
			{{ isEdit ? 'Editar Produto' : 'Novo Produto' }}
		</h1>

		<form @submit.prevent="handleSubmit" class="card">
			<div class="space-y-4">
				<div>
					<label class="label">Nome *</label>
					<input v-model="form.nome" type="text" class="input" required />
				</div>

				<div>
					<label class="label">Descrição</label>
					<textarea v-model="form.descricao" class="input" rows="3"></textarea>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="label">Preço (R$) *</label>
						<input
							v-model.number="form.preco"
							type="number"
							step="0.01"
							class="input"
							required
						/>
					</div>

					<div>
						<label class="label">Peso (kg)</label>
						<input
							v-model.number="form.peso"
							type="number"
							step="0.01"
							class="input"
						/>
					</div>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="label">Quantidade em Estoque *</label>
						<input
							v-model.number="form.quantidade_estoque"
							type="number"
							class="input"
							required
						/>
					</div>

					<div>
						<label class="label">Categoria</label>
						<input v-model="form.categoria" type="text" class="input" />
					</div>
				</div>

				<div>
					<label class="label">SKU</label>
					<input v-model="form.sku" type="text" class="input" />
				</div>

				<div v-if="error" class="p-3 bg-red-100 text-red-700 rounded-lg">
					{{ error }}
				</div>

				<div class="flex gap-4 pt-4">
					<button
						type="submit"
						:disabled="loading"
						class="btn btn-primary flex-1"
					>
						{{ loading ? 'Salvando...' : 'Salvar' }}
					</button>
					<router-link
						to="/produtos"
						class="btn btn-secondary flex-1 text-center"
					>
						Cancelar
					</router-link>
				</div>
			</div>
		</form>
	</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../../api';

const route = useRoute();
const router = useRouter();

const isEdit = computed(() => !!route.params.id);
const loading = ref(false);
const error = ref('');

const form = ref({
	nome: '',
	descricao: '',
	preco: 0,
	peso: 0,
	quantidade_estoque: 0,
	categoria: '',
	sku: '',
});

async function loadProduto() {
	if (!isEdit.value) return;

	try {
		const response = await api.get(`/produtos/${route.params.id}`);
		form.value = response.data;
	} catch (err) {
		console.error('Erro ao carregar produto:', err);
		error.value = 'Erro ao carregar produto';
	}
}

async function handleSubmit() {
	loading.value = true;
	error.value = '';

	try {
		if (isEdit.value) {
			await api.put(`/produtos/${route.params.id}`, form.value);
		} else {
			await api.post('/produtos', form.value);
		}
		router.push('/produtos');
	} catch (err) {
		console.error('Erro ao salvar produto:', err);
		error.value = err.response?.data?.detail || 'Erro ao salvar produto';
	} finally {
		loading.value = false;
	}
}

onMounted(() => {
	loadProduto();
});
</script>
