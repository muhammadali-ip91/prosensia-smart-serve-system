import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import adminApi from '../../api/adminApi'
import api from '../../api/axiosInstance'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { formatDateTime, formatMinutes, formatPercent, formatPrice } from '../../utils/formatters'

export default function AdminDashboardPage() {
	const [stats, setStats] = useState(null)
	const [health, setHealth] = useState(null)
	const [loading, setLoading] = useState(true)

	useEffect(() => {
		fetchDashboard()
		fetchSystemHealth()

		const interval = setInterval(() => {
			fetchDashboard()
		}, 5000)

		const onVisibilityChange = () => {
			if (document.visibilityState === 'visible') {
				fetchDashboard()
				fetchSystemHealth()
			}
		}

		document.addEventListener('visibilitychange', onVisibilityChange)

		return () => {
			clearInterval(interval)
			document.removeEventListener('visibilitychange', onVisibilityChange)
		}
	}, [])

	const fetchDashboard = async () => {
		try {
			const data = await adminApi.getDashboard()
			setStats(data)
		} catch (error) {
			console.error('Failed to fetch dashboard:', error)
		} finally {
			setLoading(false)
		}
	}

	const fetchSystemHealth = async () => {
		try {
			const response = await api.get('/health')
			setHealth(response.data)
		} catch (error) {
			setHealth(null)
		}
	}

	if (loading) return <LoadingSpinner size="lg" text="Loading dashboard..." />

	const getStatusClasses = (status) => {
		const normalized = (status || '').toLowerCase()
		if (normalized === 'delivered') return 'bg-green-100 text-green-700'
		if (normalized === 'ready') return 'bg-emerald-100 text-emerald-700'
		if (normalized === 'ontheway' || normalized === 'pickedup') return 'bg-blue-100 text-blue-700'
		if (normalized === 'preparing' || normalized === 'confirmed' || normalized === 'placed') return 'bg-amber-100 text-amber-700'
		if (normalized === 'cancelled' || normalized === 'rejected') return 'bg-red-100 text-red-700'
		return 'bg-gray-100 text-gray-700'
	}

	const statCards = [
		{ label: 'Orders (All Time)', value: stats?.total_orders_all_time || 0, icon: '📚', color: 'bg-slate-50 text-slate-700' },
		{ label: 'Orders Today', value: stats?.total_orders_today || 0, icon: '📦', color: 'bg-blue-50 text-blue-700' },
		{ label: 'Active Orders', value: stats?.active_orders || 0, icon: '🔄', color: 'bg-orange-50 text-orange-700' },
		{ label: 'Delivered Today', value: stats?.delivered_today || 0, icon: '✅', color: 'bg-green-50 text-green-700' },
		{ label: 'Avg Delivery', value: formatMinutes(stats?.average_delivery_time), icon: '⏱️', color: 'bg-purple-50 text-purple-700' },
		{ label: 'Runner Util.', value: formatPercent(stats?.runner_utilization), icon: '🏃', color: 'bg-teal-50 text-teal-700' },
		{ label: 'Avg Rating', value: stats?.average_rating ? `${stats.average_rating}/5 ⭐` : '-', icon: '⭐', color: 'bg-yellow-50 text-yellow-700' },
		{ label: 'AI Accuracy', value: stats?.ai_accuracy != null ? formatPercent(stats.ai_accuracy) : '-', icon: '🤖', color: 'bg-indigo-50 text-indigo-700' },
		{ label: 'AI Avg Error', value: stats?.ai_avg_error_minutes != null ? formatMinutes(stats.ai_avg_error_minutes) : '-', icon: '📊', color: 'bg-pink-50 text-pink-700' },
	]

	return (
		<div className="page-container">
			<h1 className="page-title">📊 Admin Dashboard</h1>

			{/* Stats Grid */}
			<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
				{statCards.map(stat => (
					<div key={stat.label} className={`card-compact ${stat.color} min-h-[108px] flex flex-col justify-between`}>
						<div className="flex items-center space-x-2 mb-2">
							<span className="text-2xl">{stat.icon}</span>
							<span className="text-sm font-medium opacity-80">{stat.label}</span>
						</div>
						<p className="text-2xl font-bold">{stat.value}</p>
					</div>
				))}
			</div>

			<div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
				<div className="card lg:col-span-1">
					<div className="flex items-center justify-between mb-3">
						<h2 className="text-lg font-bold text-gray-900">Active Order Ownership</h2>
						<span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full">
							Waiting: {stats?.active_orders_waiting_runner || 0}
						</span>
					</div>

					{(stats?.active_orders_by_runner || []).length === 0 ? (
						<p className="text-sm text-gray-500">No active runner assignments yet.</p>
					) : (
						<div className="space-y-2">
							{stats.active_orders_by_runner.map((runner) => (
								<div key={runner.runner_id} className="card-compact bg-gray-50">
									<div className="flex items-center justify-between gap-3">
										<div>
											<p className="font-semibold text-gray-900 text-sm">{runner.runner_name}</p>
											<p className="text-xs text-gray-500">{runner.runner_id}</p>
										</div>
										<span className="text-sm font-bold text-primary-700">{runner.active_count} active</span>
									</div>
								</div>
							))}
						</div>
					)}
				</div>

				<div className="card lg:col-span-2">
					<div className="flex items-center justify-between mb-3">
						<h2 className="text-lg font-bold text-gray-900">Live Orders (Latest 30)</h2>
						<button onClick={fetchDashboard} className="btn-secondary btn-sm">Refresh</button>
					</div>

					<div className="lg:hidden max-h-[520px] overflow-y-auto space-y-3 pr-1">
						{(stats?.recent_orders || []).map((order) => (
							<div key={order.order_id} className="card-compact bg-gray-50 border border-gray-100">
								<div className="flex items-start justify-between gap-2 mb-2">
									<p className="font-bold text-gray-900 text-sm break-words">{order.order_id}</p>
									<span className={`px-2 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${getStatusClasses(order.status)}`}>
										{order.status}
									</span>
								</div>

								<div className="grid grid-cols-2 gap-x-3 gap-y-2 text-xs">
									<div>
										<p className="text-gray-500">Customer</p>
										<p className="font-medium text-gray-900 truncate">{order.engineer_name}</p>
										<p className="text-gray-500">{order.engineer_id}</p>
									</div>
									<div>
										<p className="text-gray-500">Runner</p>
										{order.runner_id ? (
											<>
												<p className="font-medium text-gray-900 truncate">{order.runner_name || order.runner_id}</p>
												<p className="text-gray-500">{order.runner_id}</p>
											</>
										) : (
											<p className="font-medium text-orange-600">Waiting</p>
										)}
									</div>
									<div>
										<p className="text-gray-500">Station</p>
										<p className="font-medium text-gray-900">{order.station_id}</p>
									</div>
									<div>
										<p className="text-gray-500">Amount</p>
										<p className="font-medium text-gray-900">{formatPrice(order.total_price || 0)}</p>
									</div>
								</div>

								<p className="text-xs text-gray-500 mt-2">Created: {formatDateTime(order.created_at)}</p>
							</div>
						))}

						{(stats?.recent_orders || []).length === 0 && (
							<div className="card-compact text-center text-gray-500">No orders found yet.</div>
						)}
					</div>

					<div className="hidden lg:block max-h-[520px] overflow-y-auto rounded-xl border border-gray-100">
						<table className="w-full text-sm">
							<thead className="bg-gray-50 sticky top-0 z-10">
								<tr className="border-b border-gray-200 text-left text-gray-500">
									<th className="py-2 px-2">Order</th>
									<th className="py-2 px-2">Customer</th>
									<th className="py-2 px-2">Runner</th>
									<th className="py-2 px-2">Status</th>
									<th className="py-2 px-2">Station</th>
									<th className="py-2 px-2">Amount</th>
									<th className="py-2 px-2">Created</th>
								</tr>
							</thead>
							<tbody>
								{(stats?.recent_orders || []).map((order) => (
									<tr key={order.order_id} className="border-b border-gray-50 hover:bg-gray-50/70">
										<td className="py-2 px-2 font-semibold whitespace-nowrap">{order.order_id}</td>
										<td className="py-2 px-2">
											<div className="font-medium text-gray-900">{order.engineer_name}</div>
											<div className="text-xs text-gray-500">{order.engineer_id}</div>
										</td>
										<td className="py-2 px-2">
											{order.runner_id ? (
												<>
													<div className="font-medium text-gray-900">{order.runner_name || order.runner_id}</div>
													<div className="text-xs text-gray-500">{order.runner_id}</div>
												</>
											) : (
												<span className="text-orange-600 font-medium">Waiting</span>
											)}
										</td>
										<td className="py-2 px-2 whitespace-nowrap">
											<span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusClasses(order.status)}`}>
												{order.status}
											</span>
										</td>
										<td className="py-2 px-2 whitespace-nowrap">{order.station_id}</td>
										<td className="py-2 px-2 whitespace-nowrap">{formatPrice(order.total_price || 0)}</td>
										<td className="py-2 px-2 whitespace-nowrap">{formatDateTime(order.created_at)}</td>
									</tr>
								))}
								{(stats?.recent_orders || []).length === 0 && (
									<tr>
										<td colSpan={7} className="py-6 text-center text-gray-500">No orders found yet.</td>
									</tr>
								)}
							</tbody>
						</table>
					</div>
				</div>
			</div>

			<div className="card mb-8">
				<div className="flex items-center justify-between mb-4">
					<h2 className="text-lg font-bold text-gray-900">System Health</h2>
					<button onClick={fetchSystemHealth} className="btn-secondary btn-sm">Refresh</button>
				</div>

				{!health ? (
					<p className="text-sm text-gray-500">Health data unavailable</p>
				) : (
					<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
						<div className="card-compact bg-gray-50">
							<p className="text-xs text-gray-500 mb-1">Database</p>
							<p className={`font-bold ${health?.checks?.database === 'connected' ? 'text-green-600' : 'text-red-600'}`}>
								{health?.checks?.database || '-'}
							</p>
						</div>
						<div className="card-compact bg-gray-50">
							<p className="text-xs text-gray-500 mb-1">Redis</p>
							<p className={`font-bold ${health?.checks?.redis === 'connected' ? 'text-green-600' : 'text-red-600'}`}>
								{health?.checks?.redis || '-'}
							</p>
						</div>
						<div className="card-compact bg-gray-50">
							<p className="text-xs text-gray-500 mb-1">AI Model</p>
							<p className={`font-bold ${health?.checks?.ai_model === 'loaded' ? 'text-green-600' : 'text-amber-600'}`}>
								{health?.checks?.ai_model || '-'}
							</p>
						</div>
						<div className="card-compact bg-gray-50">
							<p className="text-xs text-gray-500 mb-1">Uptime</p>
							<p className="font-bold text-gray-800">{health?.checks?.uptime || '-'}</p>
						</div>
					</div>
				)}
			</div>

			{/* Quick Links */}
			<div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
				<Link to="/admin/menu" className="card hover:border-primary-300 text-center">
					<span className="text-4xl mb-2 block">🍽️</span>
					<h3 className="font-bold">Menu Management</h3>
					<p className="text-sm text-gray-500">Add, edit, delete items</p>
				</Link>
				<Link to="/admin/users" className="card hover:border-primary-300 text-center">
					<span className="text-4xl mb-2 block">👥</span>
					<h3 className="font-bold">User Management</h3>
					<p className="text-sm text-gray-500">Manage all users</p>
				</Link>
				<Link to="/kitchen" className="card hover:border-primary-300 text-center">
					<span className="text-4xl mb-2 block">🍳</span>
					<h3 className="font-bold">Kitchen View</h3>
					<p className="text-sm text-gray-500">Monitor kitchen operations</p>
				</Link>
			</div>
		</div>
	)
}
