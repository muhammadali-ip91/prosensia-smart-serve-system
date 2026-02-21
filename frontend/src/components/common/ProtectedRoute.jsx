import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

export default function ProtectedRoute({ children, allowedRoles }) {
	const { user, loading } = useAuth()

	if (loading) {
		return (
			<div className="min-h-[60vh] flex items-center justify-center">
				<div className="w-10 h-10 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
			</div>
		)
	}

	if (!user) {
		return <Navigate to="/login" replace />
	}

	if (allowedRoles && !allowedRoles.includes(user.role)) {
		// Redirect to appropriate dashboard
		const roleRedirects = {
			engineer: '/menu',
			kitchen: '/kitchen',
			runner: '/runner',
			admin: '/admin',
		}
		return <Navigate to={roleRedirects[user.role] || '/login'} replace />
	}

	return children
}
