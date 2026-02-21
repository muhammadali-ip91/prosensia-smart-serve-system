import { useState, useEffect } from 'react'
import { useSocket } from '../../hooks/useSocket'
import kitchenApi from '../../api/kitchenApi'
import menuApi from '../../api/menuApi'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { StatusBadge, PriorityBadge } from '../../components/common/Badge'
import { formatDateTime } from '../../utils/formatters'
import toast from 'react-hot-toast'

export default function KitchenDashboardPage() {
	const [data, setData] = useState(null)
	const [menuItems, setMenuItems] = useState([])
	const [menuLoading, setMenuLoading] = useState(true)
	const [reasonByItem, setReasonByItem] = useState({})
	const [kitchenSettings, setKitchenSettings] = useState(null)
	const [hoursForm, setHoursForm] = useState({ open_hour: 9, close_hour: 21 })
	const [savingHours, setSavingHours] = useState(false)
	const [togglingKitchen, setTogglingKitchen] = useState(false)
	const [loading, setLoading] = useState(true)
	const { socket } = useSocket()

	useEffect(() => {
		fetchOrders()
		fetchMenuItems()
		fetchKitchenSettings()
		const interval = setInterval(fetchOrders, 5000)
		return () => clearInterval(interval)
	}, [])

	useEffect(() => {
		if (!socket) return
		socket.on('new_order', () => {
			fetchOrders()
			// Play sound
			new Audio('/sounds/new-order.mp3').play().catch(() => {})
		})

		const onOrderStatusUpdate = () => {
			fetchOrders()
		}
		socket.on('order_status_update', onOrderStatusUpdate)

		return () => {
			socket.off('new_order')
			socket.off('order_status_update', onOrderStatusUpdate)
		}
	}, [socket])

	const fetchOrders = async () => {
		try {
			const result = await kitchenApi.getOrders()
			setData(result)
		} catch (error) {
			console.error('Failed to fetch kitchen orders:', error)
		} finally {
			setLoading(false)
		}
	}

	const handleStatusUpdate = async (orderId, newStatus) => {
		try {
			await kitchenApi.updateOrderStatus(orderId, newStatus)
			toast.success(`Order ${orderId} → ${newStatus}`)
			fetchOrders()
		} catch (error) {
			toast.error('Failed to update status')
		}
	}

	const fetchMenuItems = async () => {
		try {
			const result = await menuApi.getFullMenu()
			const flattenedItems = (result?.categories || []).flatMap(category => category.items || [])
			setMenuItems(flattenedItems)
		} catch (error) {
			console.error('Failed to fetch menu items:', error)
			toast.error('Failed to load menu items')
		} finally {
			setMenuLoading(false)
		}
	}

	const handleToggleAvailability = async (item, available) => {
		try {
			const reason = available ? null : (reasonByItem[item.item_id] || 'Out of stock')
			await kitchenApi.toggleItemAvailability(item.item_id, available, reason)
			toast.success(`${item.item_name} marked ${available ? 'available' : 'unavailable'}`)
			fetchMenuItems()
		} catch (error) {
			toast.error('Failed to update menu availability')
		}
	}

	const fetchKitchenSettings = async () => {
		try {
			const settings = await kitchenApi.getSettings()
			setKitchenSettings(settings)
			setHoursForm({
				open_hour: settings.open_hour,
				close_hour: settings.close_hour,
			})
		} catch (error) {
			toast.error('Failed to load kitchen settings')
		}
	}

	const handleSaveHours = async () => {
		setSavingHours(true)
		try {
			const openHour = parseInt(hoursForm.open_hour)
			const closeHour = parseInt(hoursForm.close_hour)
			const result = await kitchenApi.updateHours(openHour, closeHour)
			setKitchenSettings(result)
			toast.success(result.message || 'Kitchen hours updated')
		} catch (error) {
			const message = error?.response?.data?.detail?.message || 'Failed to update hours'
			toast.error(message)
		} finally {
			setSavingHours(false)
		}
	}

	const handleKitchenToggle = async (forceClosed) => {
		setTogglingKitchen(true)
		try {
			const result = await kitchenApi.toggleKitchen(forceClosed, true)
			setKitchenSettings(result)
			toast.success(result.message || (forceClosed ? 'Kitchen closed' : 'Kitchen opened'))
			fetchMenuItems()
		} catch (error) {
			const message = error?.response?.data?.detail?.message || 'Failed to update kitchen status'
			toast.error(message)
		} finally {
			setTogglingKitchen(false)
		}
	}

	if (loading) return <LoadingSpinner size="lg" text="Loading kitchen orders..." />

	return (
		<div className="page-container">
			<div className="card mb-6 sm:mb-8">
				<div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
					<div>
						<p className="text-xs font-semibold tracking-wide text-primary-600 uppercase">Kitchen Operations</p>
						<h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Kitchen Dashboard</h1>
						<p className="text-sm text-gray-500 mt-1">Track live orders and keep pickup flow smooth.</p>
					</div>
					<div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 text-xs text-gray-600">
						<span className={`w-2 h-2 rounded-full ${kitchenSettings?.is_open_now ? 'bg-green-500' : 'bg-red-500'}`} />
						{kitchenSettings?.is_open_now ? 'Kitchen Open' : 'Kitchen Closed'}
					</div>
				</div>
			</div>

			<div className="card mb-6 sm:mb-8">
				<div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
					<div>
						<h2 className="text-lg font-bold text-gray-900 mb-1">Kitchen Open/Close Control</h2>
						<p className="text-sm text-gray-500">
							Status: <span className={`font-semibold ${kitchenSettings?.is_open_now ? 'text-green-600' : 'text-red-600'}`}>
								{kitchenSettings?.is_open_now ? 'Open' : 'Closed'}
							</span>
							 {kitchenSettings?.reason ? `(${kitchenSettings.reason})` : ''}
						</p>
						<p className="text-sm text-gray-500 mt-1">
							Working Hours: {String(kitchenSettings?.open_hour ?? 9).padStart(2, '0')}:00 - {String(kitchenSettings?.close_hour ?? 21).padStart(2, '0')}:00
						</p>
					</div>

					<div className="flex gap-2">
						<button
							onClick={() => handleKitchenToggle(false)}
							disabled={togglingKitchen}
							className="btn-success btn-sm"
						>
							Open Now
						</button>
						<button
							onClick={() => handleKitchenToggle(true)}
							disabled={togglingKitchen}
							className="btn-secondary btn-sm"
						>
							Close Now
						</button>
					</div>
				</div>

				<div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4">
					<div>
						<label className="input-label">Open Hour (0-23)</label>
						<input
							type="number"
							min={0}
							max={23}
							className="input-field"
							value={hoursForm.open_hour}
							onChange={(e) => setHoursForm({ ...hoursForm, open_hour: e.target.value })}
						/>
					</div>
					<div>
						<label className="input-label">Close Hour (0-23)</label>
						<input
							type="number"
							min={0}
							max={23}
							className="input-field"
							value={hoursForm.close_hour}
							onChange={(e) => setHoursForm({ ...hoursForm, close_hour: e.target.value })}
						/>
					</div>
					<div className="sm:self-end">
						<button onClick={handleSaveHours} disabled={savingHours} className="btn-primary w-full">
							{savingHours ? 'Saving...' : 'Save Hours'}
						</button>
					</div>
				</div>
			</div>

			{/* Stats */}
			<div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
				<div className="card-compact border-l-4 border-l-blue-500">
					<p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Incoming</p>
					<p className="text-2xl sm:text-3xl font-bold text-blue-600 mt-1">{data?.counts?.incoming || 0}</p>
				</div>
				<div className="card-compact border-l-4 border-l-orange-500">
					<p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Preparing</p>
					<p className="text-2xl sm:text-3xl font-bold text-orange-600 mt-1">{data?.counts?.preparing || 0}</p>
				</div>
				<div className="card-compact border-l-4 border-l-green-500">
					<p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Ready</p>
					<p className="text-2xl sm:text-3xl font-bold text-green-600 mt-1">{data?.counts?.ready || 0}</p>
				</div>
				<div className="card-compact border-l-4 border-l-gray-500">
					<p className="text-xs font-semibold uppercase tracking-wide text-gray-500">Total Active</p>
					<p className="text-2xl sm:text-3xl font-bold text-gray-700 mt-1">{data?.counts?.total_active || 0}</p>
				</div>
			</div>

			<div className="grid grid-cols-1 xl:grid-cols-3 gap-4 sm:gap-6">
				{/* Incoming Orders */}
				<div className="card-compact">
					<div className="flex items-center justify-between mb-4">
						<h2 className="text-lg font-bold text-gray-900">📥 Incoming</h2>
						<span className="badge badge-regular">{data?.incoming?.length || 0}</span>
					</div>
					<div className="space-y-3 max-h-[30rem] overflow-y-auto pr-1">
						{data?.incoming?.length === 0 && (
							<div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 py-10 text-center text-sm text-gray-400">
								No incoming orders
							</div>
						)}
						{data?.incoming?.map(order => (
							<div key={order.order_id} className={`card-compact border ${order.priority === 'Urgent' ? 'border-red-200 bg-red-50/40' : 'border-gray-100'}`}>
								<div className="flex items-center justify-between mb-2">
									<span className="font-bold text-gray-900">{order.order_id}</span>
									<PriorityBadge priority={order.priority} />
								</div>
								<p className="text-sm text-gray-500">Station: {order.station_id}</p>
								<p className="text-xs text-gray-400">{formatDateTime(order.created_at)}</p>
								<button
									onClick={() => handleStatusUpdate(order.order_id, 'Preparing')}
									className="btn-primary btn-sm w-full mt-3"
								>
									Start Preparing
								</button>
							</div>
						))}
					</div>
				</div>

				{/* Preparing */}
				<div className="card-compact">
					<div className="flex items-center justify-between mb-4">
						<h2 className="text-lg font-bold text-gray-900">👨‍🍳 Preparing</h2>
						<span className="badge badge-regular">{data?.preparing?.length || 0}</span>
					</div>
					<div className="space-y-3 max-h-[30rem] overflow-y-auto pr-1">
						{data?.preparing?.length === 0 && (
							<div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 py-10 text-center text-sm text-gray-400">
								Nothing preparing
							</div>
						)}
						{data?.preparing?.map(order => (
							<div key={order.order_id} className="card-compact border border-orange-100 bg-orange-50/30">
								<div className="flex items-center justify-between mb-2">
									<span className="font-bold">{order.order_id}</span>
									<StatusBadge status={order.status} />
								</div>
								<p className="text-sm text-gray-500">Station: {order.station_id}</p>
								<button
									onClick={() => handleStatusUpdate(order.order_id, 'Ready')}
									className="btn-success btn-sm w-full mt-3"
								>
									✓ Mark Ready
								</button>
							</div>
						))}
					</div>
				</div>

				{/* Ready */}
				<div className="card-compact">
					<div className="flex items-center justify-between mb-4">
						<h2 className="text-lg font-bold text-gray-900">✅ Ready for Pickup</h2>
						<span className="badge badge-regular">{data?.ready?.length || 0}</span>
					</div>
					<div className="space-y-3 max-h-[30rem] overflow-y-auto pr-1">
						{data?.ready?.length === 0 && (
							<div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 py-10 text-center text-sm text-gray-400">
								Nothing ready
							</div>
						)}
						{data?.ready?.map(order => (
							<div key={order.order_id} className="card-compact border border-green-100 bg-green-50/30">
								<div className="flex items-center justify-between mb-2">
									<span className="font-bold">{order.order_id}</span>
									<StatusBadge status={order.status} />
								</div>
								<p className="text-sm text-gray-500">Runner: {order.runner_id || 'Waiting...'}</p>
							</div>
						))}
					</div>
				</div>
			</div>

			<div className="card mt-6 sm:mt-8">
				<div className="flex items-center justify-between mb-4">
					<h2 className="text-lg font-bold text-gray-900">🍽️ Manage Menu Availability</h2>
					<button onClick={fetchMenuItems} className="btn-secondary btn-sm">Refresh</button>
				</div>

				{menuLoading ? (
					<LoadingSpinner size="md" text="Loading menu..." />
				) : menuItems.length === 0 ? (
					<p className="text-gray-400 text-center py-8">No menu items found</p>
				) : (
					<div className="space-y-3 max-h-[28rem] overflow-y-auto pr-1">
						{menuItems.map(item => (
							<div key={item.item_id} className="border border-gray-200 rounded-xl p-3 bg-gray-50/40">
								<div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
									<div>
										<p className="font-semibold text-gray-900">{item.item_name}</p>
										<p className="text-xs text-gray-500">{item.category}</p>
									</div>
									<span className={`text-xs font-semibold px-2 py-1 rounded-full ${item.is_available ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
										{item.is_available ? 'Available' : 'Unavailable'}
									</span>
								</div>

								<div className="flex flex-col sm:flex-row gap-2">
									<input
										type="text"
										className="input-field flex-1"
										placeholder="Reason (e.g. Out of stock)"
										value={reasonByItem[item.item_id] || item.unavailable_reason || ''}
										onChange={(e) => setReasonByItem({ ...reasonByItem, [item.item_id]: e.target.value })}
									/>
									{item.is_available ? (
										<button
											onClick={() => handleToggleAvailability(item, false)}
											className="btn-secondary btn-sm"
										>
											Mark Unavailable
										</button>
									) : (
										<button
											onClick={() => handleToggleAvailability(item, true)}
											className="btn-success btn-sm"
										>
											Mark Available
										</button>
									)}
								</div>
							</div>
						))}
					</div>
				)}
			</div>
		</div>
	)
}
