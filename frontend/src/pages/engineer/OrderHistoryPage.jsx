import { useState, useEffect } from 'react'
import orderApi from '../../api/orderApi'
import OrderCard from '../../components/order/OrderCard'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import EmptyState from '../../components/common/EmptyState'
import { Link } from 'react-router-dom'
import { useSocket } from '../../hooks/useSocket'

export default function OrderHistoryPage() {
	const [orders, setOrders] = useState([])
	const [loading, setLoading] = useState(true)
	const [page, setPage] = useState(1)
	const [totalPages, setTotalPages] = useState(1)
	const { socket } = useSocket()

	useEffect(() => {
		fetchOrders()
	}, [page])

	useEffect(() => {
		const interval = setInterval(() => {
			fetchOrders()
		}, 6000)

		const onVisibilityChange = () => {
			if (document.visibilityState === 'visible') {
				fetchOrders()
			}
		}

		document.addEventListener('visibilitychange', onVisibilityChange)

		return () => {
			clearInterval(interval)
			document.removeEventListener('visibilitychange', onVisibilityChange)
		}
	}, [page])

	useEffect(() => {
		if (!socket) return

		const onStatusUpdate = (data) => {
			if (!data?.order_id || !data?.new_status) return
			setOrders((prev) => prev.map((order) => (
				order.order_id === data.order_id
					? { ...order, status: data.new_status, updated_at: data.updated_at || order.updated_at }
					: order
			)))
		}

		socket.on('order_status_update', onStatusUpdate)
		return () => socket.off('order_status_update', onStatusUpdate)
	}, [socket])

	const fetchOrders = async () => {
		try {
			const data = await orderApi.getMyOrders(page, 10)
			setOrders(data.orders || [])
			setTotalPages(data.total_pages || 1)
		} catch (error) {
			console.error('Failed to fetch orders:', error)
		} finally {
			setLoading(false)
		}
	}

	if (loading) return <LoadingSpinner size="lg" text="Loading orders..." />

	return (
		<div className="page-container max-w-3xl mx-auto">
			<h1 className="page-title">My Orders</h1>

			{orders.length === 0 ? (
				<EmptyState
					icon="📋"
					title="No orders yet"
					description="Place your first order from the menu"
					action={<Link to="/menu" className="btn-primary">Browse Menu</Link>}
				/>
			) : (
				<div className="space-y-4">
					{orders.map(order => (
						<OrderCard key={order.order_id} order={order} />
					))}

					{/* Pagination */}
					{totalPages > 1 && (
						<div className="flex justify-center space-x-2 pt-4">
							<button
								onClick={() => setPage(p => Math.max(1, p - 1))}
								disabled={page === 1}
								className="btn-secondary btn-sm"
							>
								Previous
							</button>
							<span className="px-4 py-2 text-sm text-gray-600">
								Page {page} of {totalPages}
							</span>
							<button
								onClick={() => setPage(p => Math.min(totalPages, p + 1))}
								disabled={page === totalPages}
								className="btn-secondary btn-sm"
							>
								Next
							</button>
						</div>
					)}
				</div>
			)}
		</div>
	)
}
