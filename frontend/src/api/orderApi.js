import api from './axiosInstance'

const orderApi = {
	placeOrder: async (orderData) => {
		const response = await api.post('/orders', orderData)
		return response.data
	},

	getOrder: async (orderId) => {
		const response = await api.get(`/orders/${orderId}`)
		return response.data
	},

	getMyOrders: async (page = 1, perPage = 20) => {
		const response = await api.get(`/orders?page=${page}&per_page=${perPage}`)
		return response.data
	},

	cancelOrder: async (orderId) => {
		const response = await api.delete(`/orders/${orderId}`)
		return response.data
	},

	submitFeedback: async (orderId, rating, comment) => {
		const response = await api.post(`/orders/${orderId}/feedback`, {
			rating,
			comment
		})
		return response.data
	},
}

export default orderApi
