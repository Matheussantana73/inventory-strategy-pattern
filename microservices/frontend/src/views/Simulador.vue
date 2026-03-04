<template>
	<div>
		<h1 class="text-3xl font-bold mb-6">🧮 Simulador de Estratégias</h1>

		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Formulário -->
			<div class="card">
				<h2 class="text-xl font-bold mb-4">Parâmetros da Simulação</h2>

				<form @submit.prevent="simular" class="space-y-4">
					<div>
						<label class="label">Valor dos Produtos (R$)</label>
						<input
							v-model.number="form.valor_produtos"
							type="number"
							step="0.01"
							class="input"
							required
						/>
					</div>

					<div>
						<label class="label">Quantidade de Itens</label>
						<input
							v-model.number="form.quantidade"
							type="number"
							class="input"
							required
						/>
					</div>

					<div>
						<label class="label">Peso Total (kg)</label>
						<input
							v-model.number="form.peso_kg"
							type="number"
							step="0.01"
							class="input"
						/>
					</div>

					<div>
						<label class="label">Distância (km)</label>
						<input
							v-model.number="form.distancia_km"
							type="number"
							step="0.1"
							class="input"
						/>
					</div>

					<div>
						<label class="label">Estratégias de Desconto</label>
						<div
							class="space-y-2 max-h-48 overflow-y-auto border rounded-lg p-3"
						>
							<label
								v-for="estrategia in estrategiasDesconto"
								:key="estrategia.tipo"
								class="flex items-center"
							>
								<input
									type="checkbox"
									:value="estrategia.tipo"
									v-model="form.estrategias_desconto"
									class="mr-2"
								/>
								<span class="text-sm">{{ estrategia.descricao }}</span>
							</label>
						</div>
					</div>

					<div>
						<label class="label">Estratégias de Frete</label>
						<div
							class="space-y-2 max-h-48 overflow-y-auto border rounded-lg p-3"
						>
							<label
								v-for="estrategia in estrategiasFrete"
								:key="estrategia.tipo"
								class="flex items-center"
							>
								<input
									type="checkbox"
									:value="estrategia.tipo"
									v-model="form.estrategias_frete"
									class="mr-2"
								/>
								<span class="text-sm">{{ estrategia.descricao }}</span>
							</label>
						</div>
					</div>

					<button
						type="submit"
						:disabled="loading"
						class="btn btn-primary w-full"
					>
						{{ loading ? 'Simulando...' : '🚀 Simular' }}
					</button>
				</form>
			</div>

			<!-- Resultados -->
			<div class="space-y-4">
				<!-- Melhor Opção -->
				<div
					v-if="resultado && resultado.melhor_opcao"
					class="card bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-500"
				>
					<div class="flex items-center gap-2 mb-4">
						<span class="text-2xl">🏆</span>
						<h2 class="text-xl font-bold">Melhor Opção</h2>
					</div>

					<div class="space-y-2">
						<div class="flex justify-between">
							<span class="text-gray-700">Desconto:</span>
							<span class="font-semibold">{{
								resultado.melhor_opcao.tipo_desconto
							}}</span>
						</div>
						<div class="flex justify-between">
							<span class="text-gray-700">Frete:</span>
							<span class="font-semibold">{{
								resultado.melhor_opcao.tipo_frete
							}}</span>
						</div>
						<hr class="my-2" />
						<div class="flex justify-between">
							<span>Valor dos produtos:</span>
							<span
								>R$ {{ resultado.melhor_opcao.valor_produtos.toFixed(2) }}</span
							>
						</div>
						<div class="flex justify-between text-green-600">
							<span>Desconto:</span>
							<span>- R$ {{ resultado.melhor_opcao.desconto.toFixed(2) }}</span>
						</div>
						<div class="flex justify-between">
							<span>Frete:</span>
							<span>R$ {{ resultado.melhor_opcao.frete.toFixed(2) }}</span>
						</div>
						<hr class="my-2 border-green-300" />
						<div class="flex justify-between text-2xl font-bold">
							<span>Total:</span>
							<span class="text-green-600"
								>R$ {{ resultado.melhor_opcao.valor_final.toFixed(2) }}</span
							>
						</div>
					</div>
				</div>

				<!-- Todas as Opções -->
				<div v-if="resultado && resultado.resultados" class="card">
					<h2 class="text-xl font-bold mb-4">
						Todas as Combinações ({{ resultado.resultados.length }})
					</h2>

					<div class="space-y-3 max-h-[600px] overflow-y-auto">
						<div
							v-for="(opcao, index) in resultado.resultados"
							:key="index"
							class="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
						>
							<div class="flex justify-between items-start mb-2">
								<div class="text-sm">
									<p class="font-semibold">{{ opcao.tipo_desconto }}</p>
									<p class="text-gray-600">{{ opcao.tipo_frete }}</p>
								</div>
								<div class="text-right">
									<p class="text-xl font-bold text-blue-600">
										R$ {{ opcao.valor_final.toFixed(2) }}
									</p>
									<p
										v-if="opcao.percentual_desconto > 0"
										class="text-xs text-green-600"
									>
										-{{ opcao.percentual_desconto.toFixed(1) }}% desconto
									</p>
								</div>
							</div>

							<div class="text-xs text-gray-600 grid grid-cols-3 gap-2">
								<div>Produtos: R$ {{ opcao.valor_produtos.toFixed(2) }}</div>
								<div>Desc: R$ {{ opcao.desconto.toFixed(2) }}</div>
								<div>Frete: R$ {{ opcao.frete.toFixed(2) }}</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const loading = ref(false);
const estrategiasDesconto = ref([]);
const estrategiasFrete = ref([]);
const resultado = ref(null);

const form = ref({
	valor_produtos: 1000,
	quantidade: 5,
	peso_kg: 10,
	distancia_km: 50,
	estrategias_desconto: ['sem_desconto', 'percentual_10', 'percentual_20'],
	estrategias_frete: ['fixo_30', 'fixo_50', 'por_peso'],
});

async function carregarEstrategias() {
	try {
		const response = await api.get('/estrategias');
		estrategiasDesconto.value = response.data.desconto;
		estrategiasFrete.value = response.data.frete;
	} catch (error) {
		console.error('Erro ao carregar estratégias:', error);
	}
}

async function simular() {
	if (
		form.value.estrategias_desconto.length === 0 ||
		form.value.estrategias_frete.length === 0
	) {
		alert('Selecione pelo menos uma estratégia de desconto e uma de frete');
		return;
	}

	loading.value = true;
	try {
		const response = await api.post('/simular', form.value);
		resultado.value = response.data;
	} catch (error) {
		console.error('Erro ao simular:', error);
		alert('Erro ao realizar simulação');
	} finally {
		loading.value = false;
	}
}

onMounted(() => {
	carregarEstrategias();
});
</script>
