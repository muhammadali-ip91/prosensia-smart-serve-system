import api from './axiosInstance'

const notificationApi = {
	getNotifications: async (unreadOnly = false, limit = 50) => {
		const response = await api.get(
			`/notifications?unread_only=${unreadOnly}&limit=${limit}`
		)
		return response.data
	},

	markAsRead: async (notificationIds) => {
		const response = await api.patch('/notifications/read', {
			notification_ids: notificationIds
		})
		return response.data
	},
}

export default notificationApi
