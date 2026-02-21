import { useState, useEffect } from 'react'
import { useSocket } from '../../hooks/useSocket'
import runnerApi from '../../api/runnerApi'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { StatusBadge, PriorityBadge } from '../../components/common/Badge'
import { RUNNER_STATUS } from '../../utils/constants'
import toast from 'react-hot-toast'

export default function RunnerDashboardPage() {
	const [data, setData] = useState(null)
	const [loading, setLoading] = useState(true)
	const [myStatus, setMyStatus] = useState('Available')
	const { socket } = useSocket()

	useEffect(() => {
		fetchDeliveries()
		const interval = setInterval(fetchDeliveries, 5000)
		return () => clearInterval(interval)
	}, [])

	useEffect(() => {
		if (!socket) return
		socket.on('new_delivery', () => {
			fetchDeliveries()
			new Audio('/sounds/new-order.mp3').play().catch(() => {})
			toast('🚀 New delivery assigned!', {
				id: 'runner-new-delivery',
				icon: '📦',
				duration: 2200,
			})
		})

		const onOrderStatusUpdate = () => {
			fetchDeliveries()
		}
		socket.on('order_status_update', onOrderStatusUpdate)

		return () => {
			socket.off('new_delivery')
			socket.off('order_status_update', onOrderStatusUpdate)
		}
	}, [socket])

	const fetchDeliveries = async () => {
		try {
			const result = await runnerApi.getDeliveries()
			setData(result)
			if (result?.current_status) {
				setMyStatus(result.current_status)
			}
		} catch (error) {
			console.error('Failed to fetch deliveries:', error)
		} finally {
			setLoading(false)
		}
	}

	const handleStatusUpdate = async (orderId, newStatus) => {
		try {
			await runnerApi.updateDeliveryStatus(orderId, newStatus)
			toast.success(`Delivery ${orderId} → ${newStatus}`, {
				id: `runner-delivery-${orderId}`,
				duration: 1800,
			})
			fetchDeliveries()
		} catch (error) {
			toast.error('Failed to update', { id: 'runner-update-error' })
		}
	}

	const handleAvailabilityChange = async (status) => {
		try {
			await runnerApi.updateAvailability(status)
			setMyStatus(status)
			toast.success(`Status: ${status}`, {
				id: 'runner-status',
				duration: 1600,
			})
		} catch (error) {
			toast.error('Failed to update status', { id: 'runner-status-error' })
		}
	}

	if (loading) return <LoadingSpinner size="lg" text="Loading deliveries..." />

	return (
		<div className="page-container max-w-2xl mx-auto">
			<h1 className="page-title">🏃 Runner Dashboard</h1>

			{/* Status Toggle */}
			<div className="card mb-6">
				<p className="text-sm font-medium text-gray-600 mb-3">My Status</p>
				<div className="flex space-x-2">
					{Object.values(RUNNER_STATUS).map(status => (
						<button
							key={status}
							onClick={() => handleAvailabilityChange(status)}
							className={`flex-1 py-2.5 rounded-lg text-sm font-medium border-2 transition-all ${
								myStatus === status
									? status === 'Available' ? 'border-green-500 bg-green-50 text-green-700'
										: status === 'Busy' ? 'border-orange-500 bg-orange-50 text-orange-700'
										: 'border-gray-500 bg-gray-50 text-gray-700'
									: 'border-gray-200 text-gray-400 hover:border-gray-300'
							}`}
						>
							{status === 'Available' ? '🟢' : status === 'Busy' ? '🟡' : '🔴'} {status}
						</button>
					))}
				</div>
			</div>

			{/* Stats */}
			<div className="grid grid-cols-2 gap-4 mb-6">
				<div className="card-compact text-center">
					<p className="text-3xl font-bold text-primary-600">{data?.active_count || 0}</p>
					<p className="text-sm text-gray-500">Active Deliveries</p>
				</div>
				<div className="card-compact text-center">
					<p className="text-3xl font-bold text-green-600">{data?.completed_today || 0}</p>
					<p className="text-sm text-gray-500">Completed Today</p>
				</div>
			</div>

			{/* Active Deliveries */}
			<h2 className="text-lg font-bold text-gray-900 mb-3">Active Deliveries</h2>
			{data?.active_deliveries?.length === 0 ? (
				<div className="card text-center py-12">
					<div className="text-5xl mb-4">📭</div>
					<p className="text-gray-500">No active deliveries</p>
				</div>
			) : (
				<div className="space-y-4">
					{data?.active_deliveries?.map(order => (
						<div key={order.order_id} className={`card ${order.priority === 'Urgent' ? 'border-l-4 border-l-red-500' : 'border-l-4 border-l-primary-500'}`}>
							<div className="flex items-center justify-between mb-2">
								<span className="font-bold text-lg">{order.order_id}</span>
								<div className="flex space-x-2">
									<PriorityBadge priority={order.priority} />
									<StatusBadge status={order.status} />
								</div>
							</div>

							<p className="text-sm text-gray-600 mb-1">📍 Deliver to: <span className="font-semibold">{order.station_id}</span></p>
							{order.special_instructions && (
								<p className="text-sm text-gray-500 italic mb-3">📝 {order.special_instructions}</p>
							)}

							{/* Action Buttons */}
							<div className="flex space-x-2 mt-3">
								{order.status === 'Ready' && (
									<button onClick={() => handleStatusUpdate(order.order_id, 'PickedUp')} className="btn-primary btn-sm flex-1">
										📦 Pick Up
									</button>
								)}
								{order.status === 'PickedUp' && (
									<button onClick={() => handleStatusUpdate(order.order_id, 'OnTheWay')} className="btn-primary btn-sm flex-1">
										🚶 On The Way
									</button>
								)}
								{order.status === 'OnTheWay' && (
									<button onClick={() => handleStatusUpdate(order.order_id, 'Delivered')} className="btn-success btn-sm flex-1">
										✅ Delivered
									</button>
								)}
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	)
}
