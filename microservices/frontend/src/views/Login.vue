<template>
	<div
		class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600"
	>
		<div class="card max-w-md w-full">
			<h1 class="text-3xl font-bold text-center mb-8">Sistema de Estoque</h1>

			<form @submit.prevent="handleLogin">
				<div class="mb-4">
					<label class="label">Email</label>
					<input
						v-model="email"
						type="email"
						class="input"
						placeholder="seu@email.com"
						required
					/>
				</div>

				<div class="mb-6">
					<label class="label">Senha</label>
					<input
						v-model="senha"
						type="password"
						class="input"
						placeholder="••••••••"
						required
					/>
				</div>

				<div v-if="error" class="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
					{{ error }}
				</div>

				<button
					type="submit"
					:disabled="loading"
					class="btn btn-primary w-full"
				>
					{{ loading ? 'Entrando...' : 'Entrar' }}
				</button>
			</form>

			<div class="mt-6 p-4 bg-gray-100 rounded-lg">
				<p class="text-sm text-gray-600 text-center">
					<strong>Usuário padrão:</strong><br />
					Email: admin@estoque.com<br />
					Senha: admin123
				</p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('admin@estoque.com');
const senha = ref('admin123');
const loading = ref(false);
const error = ref('');

async function handleLogin() {
	loading.value = true;
	error.value = '';

	try {
		await authStore.login(email.value, senha.value);
		router.push('/');
	} catch (err) {
		error.value = err.response?.data?.detail || 'Erro ao fazer login';
	} finally {
		loading.value = false;
	}
}
</script>
