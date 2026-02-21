import { createContext, useState, useEffect, useCallback } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useSocket } from '../hooks/useSocket'
import notificationApi from '../api/notificationApi'
import toast from 'react-hot-toast'

export const NotificationContext = createContext(null)

export function NotificationProvider({ children }) {
	const [notifications, setNotifications] = useState([])
	const [unreadCount, setUnreadCount] = useState(0)
	const { user } = useAuth()
	const { socket } = useSocket()

	// Fetch notifications on mount
	useEffect(() => {
		if (user) {
			fetchNotifications()
		}
	}, [user])

	// Listen for real-time notifications
	useEffect(() => {
		if (!socket) return

		socket.on('notification', (data) => {
			setNotifications(prev => [data, ...prev])
			setUnreadCount(prev => prev + 1)

			// Show toast
			toast(data.message, {
				id: `notif-${data.notification_id || data.type || Date.now()}`,
				icon: data.priority === 'high' ? '🔴' : 'ℹ️',
				duration: 2600,
			})

			// Play sound
			playNotificationSound(data.priority)
		})

		socket.on('order_status_update', (data) => {
			if (user?.role !== 'engineer') return
			toast.success(`Order ${data.order_id}: ${data.new_status}`, {
				id: `order-status-${data.order_id}`,
				duration: 2400,
			})
		})

		return () => {
			socket.off('notification')
			socket.off('order_status_update')
		}
	}, [socket, user?.role])

	const fetchNotifications = async () => {
		try {
			const data = await notificationApi.getNotifications()
			setNotifications(data.notifications || [])
			setUnreadCount(data.unread_count || 0)
		} catch (error) {
			console.error('Failed to fetch notifications:', error)
		}
	}

	const markAsRead = useCallback(async (ids) => {
		try {
			await notificationApi.markAsRead(ids)
			setNotifications(prev =>
				prev.map(n =>
					ids.includes(n.notification_id)
						? { ...n, is_read: true }
						: n
				)
			)
			setUnreadCount(prev => Math.max(0, prev - ids.length))
		} catch (error) {
			console.error('Failed to mark as read:', error)
		}
	}, [])

	const markAllAsRead = useCallback(async () => {
		const unreadIds = notifications
			.filter(n => !n.is_read)
			.map(n => n.notification_id)

		if (unreadIds.length > 0) {
			await markAsRead(unreadIds)
		}
	}, [notifications, markAsRead])

	const playNotificationSound = (priority) => {
		try {
			const audioFile = priority === 'high'
				? '/sounds/urgent-alert.mp3'
				: '/sounds/notification.mp3'
			const audio = new Audio(audioFile)
			audio.volume = 0.5
			audio.play().catch(() => {}) // Ignore autoplay errors
		} catch (e) {
			// Audio not supported
		}
	}

	const value = {
		notifications,
		unreadCount,
		markAsRead,
		markAllAsRead,
		refreshNotifications: fetchNotifications,
	}

	return (
		<NotificationContext.Provider value={value}>
			{children}
		</NotificationContext.Provider>
	)
}
