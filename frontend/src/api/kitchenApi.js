import api from './axiosInstance'

const kitchenApi = {
	getOrders: async () => {
		const response = await api.get('/kitchen/orders')
		return response.data
	},

	updateOrderStatus: async (orderId, status) => {
		const response = await api.patch(`/kitchen/orders/${orderId}/status`, {
			status
		})
		return response.data
	},

	toggleItemAvailability: async (itemId, available, reason = null) => {
		const response = await api.patch(`/kitchen/menu/${itemId}/availability`, {
			available,
			reason
		})
		return response.data
	},

	getSettings: async () => {
		const response = await api.get('/kitchen/settings')
		return response.data
	},

	updateHours: async (openHour, closeHour) => {
		const response = await api.patch('/kitchen/settings/hours', {
			open_hour: openHour,
			close_hour: closeHour,
		})
		return response.data
	},

	toggleKitchen: async (forceClosed, applyToAllMenu = true) => {
		const response = await api.patch('/kitchen/settings/toggle', {
			force_closed: forceClosed,
			apply_to_all_menu: applyToAllMenu,
		})
		return response.data
	},
}

export default kitchenApi
