import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../api';

export const useAuthStore = defineStore('auth', () => {
	const user = ref(null);
	const accessToken = ref(localStorage.getItem('access_token'));
	const refreshToken = ref(localStorage.getItem('refresh_token'));

	const isAuthenticated = computed(() => !!accessToken.value);

	async function login(email, senha) {
		try {
			const response = await api.post('/auth/login', { email, senha });
			accessToken.value = response.data.access_token;
			refreshToken.value = response.data.refresh_token;

			localStorage.setItem('access_token', response.data.access_token);
			localStorage.setItem('refresh_token', response.data.refresh_token);

			await fetchUser();
			return true;
		} catch (error) {
			console.error('Erro no login:', error);
			throw error;
		}
	}

	async function fetchUser() {
		try {
			const response = await api.get('/auth/me');
			user.value = response.data;
		} catch (error) {
			console.error('Erro ao buscar usuário:', error);
		}
	}

	async function logout() {
		try {
			await api.post('/auth/logout');
		} catch (error) {
			console.error('Erro no logout:', error);
		} finally {
			user.value = null;
			accessToken.value = null;
			refreshToken.value = null;
			localStorage.removeItem('access_token');
			localStorage.removeItem('refresh_token');
		}
	}

	function checkAuth() {
		if (accessToken.value) {
			fetchUser();
		}
	}

	return {
		user,
		isAuthenticated,
		login,
		logout,
		checkAuth,
		fetchUser,
	};
});
