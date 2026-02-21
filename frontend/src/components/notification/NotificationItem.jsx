import { useNavigate } from 'react-router-dom'
import { useNotification } from '../../hooks/useNotification'
import { timeAgo } from '../../utils/formatters'

export default function NotificationItem({ notification, onClose }) {
	const { markAsRead } = useNotification()
	const navigate = useNavigate()

	const handleClick = () => {
		if (!notification.is_read) {
			markAsRead([notification.notification_id])
		}

		if (notification.action_url) {
			navigate(notification.action_url)
			onClose()
		}
	}

	const priorityIcons = {
		high: '🔴',
		normal: '🔵',
		low: '⚪',
	}

	return (
		<div
			onClick={handleClick}
			className={`px-4 py-3 border-b border-gray-50 cursor-pointer transition-colors hover:bg-gray-50 ${
				!notification.is_read ? 'bg-primary-50/50' : ''
			}`}
		>
			<div className="flex items-start space-x-3">
				<span className="text-lg mt-0.5">
					{priorityIcons[notification.priority] || '🔵'}
				</span>
				<div className="flex-1 min-w-0">
					<p className={`text-sm ${!notification.is_read ? 'font-semibold' : 'font-medium'} text-gray-900`}>
						{notification.title}
					</p>
					<p className="text-sm text-gray-500 mt-0.5 truncate">
						{notification.message}
					</p>
					<p className="text-xs text-gray-400 mt-1">
						{timeAgo(notification.created_at)}
					</p>
				</div>
				{!notification.is_read && (
					<div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
				)}
			</div>
		</div>
	)
}
