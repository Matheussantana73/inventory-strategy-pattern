<template>
	<div>
		<div class="flex justify-between items-center mb-6">
			<h1 class="text-3xl font-bold">Produtos</h1>
			<router-link to="/produtos/novo" class="btn btn-primary">
				➕ Novo Produto
			</router-link>
		</div>

		<div class="card mb-6">
			<div class="flex gap-4">
				<input
					v-model="search"
					type="text"
					placeholder="Buscar por nome ou SKU..."
					class="input flex-1"
					@input="loadProdutos"
				/>
				<select v-model="categoria" class="input" @change="loadProdutos">
					<option value="">Todas as categorias</option>
					<option v-for="cat in categorias" :key="cat" :value="cat">
						{{ cat }}
					</option>
				</select>
			</div>
		</div>

		<div v-if="loading" class="text-center py-8">
			<p class="text-gray-600">Carregando produtos...</p>
		</div>

		<div
			v-else-if="produtos.length"
			class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
		>
			<div
				v-for="produto in produtos"
				:key="produto.id"
				class="card hover:shadow-lg transition-shadow"
			>
				<div class="flex justify-between items-start mb-4">
					<h3 class="text-xl font-bold">{{ produto.nome }}</h3>
					<span
						:class="
							produto.quantidade_estoque > 0
								? 'bg-green-100 text-green-800'
								: 'bg-red-100 text-red-800'
						"
						class="px-2 py-1 rounded text-xs font-semibold"
					>
						{{ produto.quantidade_estoque }} em estoque
					</span>
				</div>

				<p v-if="produto.descricao" class="text-gray-600 text-sm mb-3">
					{{ produto.descricao }}
				</p>

				<div class="flex items-center justify-between mb-4">
					<p class="text-2xl font-bold text-blue-600">
						R$ {{ parseFloat(produto.preco).toFixed(2) }}
					</p>
					<p class="text-sm text-gray-500">{{ produto.peso }} kg</p>
				</div>

				<div class="flex gap-2">
					<router-link
						:to="`/produtos/${produto.id}/editar`"
						class="btn btn-secondary flex-1 text-center text-sm"
					>
						✏️ Editar
					</router-link>
					<button
						@click="deletarProduto(produto)"
						class="btn btn-danger flex-1 text-sm"
					>
						🗑️ Excluir
					</button>
				</div>
			</div>
		</div>

		<p v-else class="text-center text-gray-500 py-8">
			Nenhum produto encontrado
		</p>

		<div v-if="totalPages > 1" class="flex justify-center gap-2 mt-8">
			<button
				v-for="page in totalPages"
				:key="page"
				@click="
					currentPage = page;
					loadProdutos();
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
import api from '../../api';

const produtos = ref([]);
const categorias = ref([]);
const loading = ref(false);
const search = ref('');
const categoria = ref('');
const currentPage = ref(1);
const totalPages = ref(1);

async function loadProdutos() {
	loading.value = true;
	try {
		const params = {
			page: currentPage.value,
			per_page: 9,
		};

		if (search.value) params.search = search.value;
		if (categoria.value) params.categoria = categoria.value;

		const response = await api.get('/produtos', { params });
		produtos.value = response.data.items;
		totalPages.value = response.data.pages;

		// Extrair categorias únicas
		const cats = new Set(
			response.data.items.map((p) => p.categoria).filter(Boolean),
		);
		categorias.value = Array.from(cats);
	} catch (error) {
		console.error('Erro ao carregar produtos:', error);
		alert('Erro ao carregar produtos');
	} finally {
		loading.value = false;
	}
}

async function deletarProduto(produto) {
	if (!confirm(`Tem certeza que deseja excluir "${produto.nome}"?`)) return;

	try {
		await api.delete(`/produtos/${produto.id}`);
		await loadProdutos();
	} catch (error) {
		console.error('Erro ao deletar produto:', error);
		alert('Erro ao deletar produto');
	}
}

onMounted(() => {
	loadProdutos();
});
</script>
