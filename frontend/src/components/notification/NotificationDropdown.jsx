import { useNotification } from '../../hooks/useNotification'
import NotificationItem from './NotificationItem'

export default function NotificationDropdown({ onClose }) {
	const { notifications, unreadCount, markAllAsRead } = useNotification()

	return (
		<div className="absolute right-0 mt-2 w-[calc(100vw-1rem)] max-w-sm sm:max-w-md bg-white rounded-xl shadow-xl border border-gray-200 z-50 animate-slide-in">
			{/* Header */}
			<div className="flex items-center justify-between p-4 border-b border-gray-100">
				<h3 className="font-bold text-gray-900">
					Notifications {unreadCount > 0 && `(${unreadCount})`}
				</h3>
				{unreadCount > 0 && (
					<button
						onClick={markAllAsRead}
						className="text-sm text-primary-600 hover:text-primary-700 font-medium"
					>
						Mark all read
					</button>
				)}
			</div>

			{/* Notifications List */}
			<div className="max-h-96 overflow-y-auto">
				{notifications.length === 0 ? (
					<div className="p-8 text-center text-gray-500">
						<div className="text-4xl mb-2">🔔</div>
						<p>No notifications yet</p>
					</div>
				) : (
					notifications.slice(0, 20).map(notif => (
						<NotificationItem
							key={notif.notification_id}
							notification={notif}
							onClose={onClose}
						/>
					))
				)}
			</div>
		</div>
	)
}
