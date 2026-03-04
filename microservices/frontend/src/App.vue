<template>
	<div id="app" class="min-h-screen">
		<Navbar v-if="authStore.isAuthenticated" />
		<main class="container mx-auto px-4 py-8">
			<router-view />
		</main>
	</div>
</template>

<script setup>
import { onMounted } from 'vue';
import Navbar from './components/Navbar.vue';
import { useAuthStore } from './stores/auth';

const authStore = useAuthStore();

onMounted(() => {
	authStore.checkAuth();
});
</script>
