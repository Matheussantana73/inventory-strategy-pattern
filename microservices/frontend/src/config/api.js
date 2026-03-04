/**
 * Configuração de URLs das APIs
 * Utiliza variáveis de ambiente do Vite
 */

// URLs dos microserviços (definidas no .env ou variáveis de ambiente do Render)
export const API_URLS = {
	auth: import.meta.env.VITE_AUTH_SERVICE_URL || 'http://localhost:8004',
	produto: import.meta.env.VITE_PRODUTO_SERVICE_URL || 'http://localhost:8001',
	pedido: import.meta.env.VITE_PEDIDO_SERVICE_URL || 'http://localhost:8002',
	calculo: import.meta.env.VITE_CALCULO_SERVICE_URL || 'http://localhost:8003',
};

// Verificar se está em desenvolvimento
export const isDevelopment = import.meta.env.DEV;

// Se estiver usando Docker local, todas as requisições vão para /api/v1
export const USE_API_GATEWAY = import.meta.env.VITE_USE_API_GATEWAY === 'true';

// Base URL para modo gateway (Docker local com nginx)
export const GATEWAY_BASE_URL = '/api/v1';

/**
 * Retorna a URL base para um serviço específico
 * @param {string} service - Nome do serviço (auth, produto, pedido, calculo)
 * @returns {string} URL base do serviço
 */
export function getServiceUrl(service) {
	if (USE_API_GATEWAY) {
		return GATEWAY_BASE_URL;
	}
	return API_URLS[service] || API_URLS.auth;
}

/**
 * Monta a URL completa para um endpoint
 * @param {string} service - Nome do serviço
 * @param {string} path - Caminho do endpoint (ex: /login)
 * @returns {string} URL completa
 */
export function buildUrl(service, path) {
	const baseUrl = getServiceUrl(service);
	const cleanPath = path.startsWith('/') ? path : `/${path}`;
	return `${baseUrl}${cleanPath}`;
}

export default {
	API_URLS,
	getServiceUrl,
	buildUrl,
	isDevelopment,
};
