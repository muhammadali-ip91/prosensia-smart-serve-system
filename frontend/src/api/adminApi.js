import api from './axiosInstance'

const adminApi = {
	getDashboard: async () => {
		const response = await api.get('/admin/dashboard')
		return response.data
	},

	getPopularItems: async (limit = 10) => {
		const response = await api.get(`/admin/popular-items?limit=${limit}`)
		return response.data
	},

	// Menu Management
	addMenuItem: async (itemData) => {
		const response = await api.post('/admin/menu', itemData)
		return response.data
	},

	uploadMenuImage: async (imageFile) => {
		const formData = new FormData()
		formData.append('image', imageFile)
		const response = await api.post('/admin/menu/upload-image', formData)
		return response.data
	},

	updateMenuItem: async (itemId, itemData) => {
		const response = await api.put(`/admin/menu/${itemId}`, itemData)
		return response.data
	},

	deleteMenuItem: async (itemId) => {
		const response = await api.delete(`/admin/menu/${itemId}`)
		return response.data
	},

	// User Management
	getUsers: async (role = null) => {
		const url = role ? `/admin/users?role=${role}` : '/admin/users'
		const response = await api.get(url)
		return response.data
	},

	addUser: async (userData) => {
		const response = await api.post('/admin/users', userData)
		return response.data
	},

	updateUser: async (userId, userData) => {
		const response = await api.put(`/admin/users/${userId}`, userData)
		return response.data
	},

	toggleUser: async (userId, active) => {
		const response = await api.put(`/admin/users/${userId}/toggle?active=${active}`)
		return response.data
	},
}

export default adminApi
