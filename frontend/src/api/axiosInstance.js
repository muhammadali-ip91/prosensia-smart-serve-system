import axios from 'axios'
import toast from 'react-hot-toast'

const resolveApiHost = () => {
	if (typeof window === 'undefined') return 'localhost'

	const host = window.location.hostname
	if (!host || host === '0.0.0.0' || host === '::' || host === '[::]') {
		return 'localhost'
	}

	return host
}

const defaultApiUrl = typeof window !== 'undefined'
	? `${window.location.protocol}//${resolveApiHost()}:8000`
	: 'http://localhost:8000'

const API_URL = import.meta.env.VITE_API_URL || defaultApiUrl

// Create Axios instance
const api = axios.create({
	baseURL: API_URL,
	timeout: 15000,
})

// ============================================
// REQUEST INTERCEPTOR
// ============================================
api.interceptors.request.use(
	(config) => {
		// Add JWT token to every request
		const token = localStorage.getItem('access_token')
		if (token) {
			config.headers.Authorization = `Bearer ${token}`
		}
		return config
	},
	(error) => {
		return Promise.reject(error)
	}
)

// ============================================
// RESPONSE INTERCEPTOR
// ============================================
api.interceptors.response.use(
	(response) => {
		return response
	},
	async (error) => {
		const originalRequest = error.config

		// ---- Handle 401 (Token Expired) ----
		if (error.response?.status === 401 && !originalRequest._retry) {
			originalRequest._retry = true

			try {
				const refreshToken = localStorage.getItem('refresh_token')

				if (refreshToken) {
					// Try to refresh the token
					const response = await axios.post(`${API_URL}/auth/refresh`, {
						refresh_token: refreshToken
					})

					const { access_token } = response.data
					localStorage.setItem('access_token', access_token)

					// Retry original request with new token
					originalRequest.headers.Authorization = `Bearer ${access_token}`
					return api(originalRequest)
				}
			} catch (refreshError) {
				// Refresh failed - logout
				localStorage.removeItem('access_token')
				localStorage.removeItem('refresh_token')
				localStorage.removeItem('user')
				window.location.href = '/login'
				return Promise.reject(refreshError)
			}
		}

		// ---- Handle 403 (Forbidden) ----
		if (error.response?.status === 403) {
			toast.error('Access denied. You do not have permission.')
		}

		// ---- Handle 429 (Rate Limited) ----
		if (error.response?.status === 429) {
			toast.error('Too many requests. Please slow down.')
		}

		// ---- Handle 500 (Server Error) ----
		if (error.response?.status >= 500) {
			toast.error('Server error. Please try again later.')
		}

		// ---- Handle Network Error ----
		if (!error.response) {
			toast.error('Network error. Please check your connection.')
		}

		return Promise.reject(error)
	}
)

export default api
