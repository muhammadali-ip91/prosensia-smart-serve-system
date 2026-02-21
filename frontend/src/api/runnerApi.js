import api from './axiosInstance'

const runnerApi = {
	getDeliveries: async () => {
		const response = await api.get('/runner/deliveries')
		return response.data
	},

	updateDeliveryStatus: async (orderId, status) => {
		const response = await api.patch(`/runner/deliveries/${orderId}/status`, {
			status
		})
		return response.data
	},

	updateAvailability: async (status) => {
		const response = await api.patch('/runner/status', { status })
		return response.data
	},
}

export default runnerApi
