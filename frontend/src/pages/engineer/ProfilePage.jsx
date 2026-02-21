import { useAuth } from '../../hooks/useAuth'
import { formatDateTime } from '../../utils/formatters'
import { getInitials } from '../../utils/helpers'
import Badge from '../../components/common/Badge'

export default function ProfilePage() {
	const { user } = useAuth()

	const roleColors = {
		engineer: 'primary',
		kitchen: 'warning',
		runner: 'success',
		admin: 'danger',
	}

	return (
		<div className="page-container max-w-lg mx-auto">
			<div className="card text-center">
				{/* Avatar */}
				<div className="w-24 h-24 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-3xl font-bold mx-auto mb-4">
					{getInitials(user?.name)}
				</div>

				<h1 className="text-2xl font-bold text-gray-900">{user?.name}</h1>
				<p className="text-gray-500 mb-2">{user?.email}</p>
				<Badge text={user?.role?.toUpperCase()} variant={roleColors[user?.role] || 'default'} size="md" />

				{/* Details */}
				<div className="mt-6 space-y-3 text-left">
					<div className="flex justify-between py-2 border-b border-gray-100">
						<span className="text-gray-500">User ID</span>
						<span className="font-medium">{user?.user_id}</span>
					</div>
					<div className="flex justify-between py-2 border-b border-gray-100">
						<span className="text-gray-500">Department</span>
						<span className="font-medium">{user?.department || '-'}</span>
					</div>
					<div className="flex justify-between py-2 border-b border-gray-100">
						<span className="text-gray-500">Phone</span>
						<span className="font-medium">{user?.phone || '-'}</span>
					</div>
					<div className="flex justify-between py-2">
						<span className="text-gray-500">Status</span>
						<Badge text={user?.is_active ? 'Active' : 'Inactive'} variant={user?.is_active ? 'success' : 'danger'} />
					</div>
				</div>
			</div>
		</div>
	)
}
