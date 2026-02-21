import api from './axiosInstance'

const authApi = {
	login: async (email, password) => {
		const response = await api.post('/auth/login', { email, password })
		return response.data
	},

	refresh: async (refreshToken) => {
		const response = await api.post('/auth/refresh', {
			refresh_token: refreshToken
		})
		return response.data
	},

	getMe: async () => {
		const response = await api.get('/auth/me')
		return response.data
	},

	logout: async () => {
		const response = await api.post('/auth/logout')
		return response.data
	},
}

export default authApi
