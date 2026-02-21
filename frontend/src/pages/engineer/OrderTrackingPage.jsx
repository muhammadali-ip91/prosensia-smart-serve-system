import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useSocket } from '../../hooks/useSocket'
import orderApi from '../../api/orderApi'
import ProgressBar from '../../components/order/ProgressBar'
import ETADisplay from '../../components/order/ETADisplay'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { StatusBadge, PriorityBadge } from '../../components/common/Badge'
import TriviaPopup from '../../components/trivia/TriviaPopup'
import { formatDateTime, formatPrice } from '../../utils/formatters'

export default function OrderTrackingPage() {
	const { orderId } = useParams()
	const { socket } = useSocket()
	const [order, setOrder] = useState(null)
	const [loading, setLoading] = useState(true)
	const [showTrivia, setShowTrivia] = useState(false)

	useEffect(() => {
		fetchOrder()
	}, [orderId])

	useEffect(() => {
		const interval = setInterval(() => {
			fetchOrder()
		}, 4000)

		const onVisibilityChange = () => {
			if (document.visibilityState === 'visible') {
				fetchOrder()
			}
		}

		document.addEventListener('visibilitychange', onVisibilityChange)

		return () => {
			clearInterval(interval)
			document.removeEventListener('visibilitychange', onVisibilityChange)
		}
	}, [orderId])

	// Listen for real-time updates
	useEffect(() => {
		if (!socket) return

		socket.on('order_status_update', (data) => {
			if (data.order_id === orderId) {
				setOrder(prev => ({
					...prev,
					status: data.new_status,
					ai_predicted_eta: data.updated_eta || prev?.ai_predicted_eta
				}))
			}
		})

		socket.on('eta_update', (data) => {
			if (data.order_id === orderId) {
				setOrder(prev => ({
					...prev,
					ai_predicted_eta: data.new_eta
				}))
			}
		})

		return () => {
			socket.off('order_status_update')
			socket.off('eta_update')
		}
	}, [socket, orderId])

	// Show trivia during preparation
	useEffect(() => {
		if (order?.status === 'Preparing' || order?.status === 'Ready') {
			setShowTrivia(true)
		} else {
			setShowTrivia(false)
		}
	}, [order?.status])

	const fetchOrder = async () => {
		try {
			const data = await orderApi.getOrder(orderId)
			setOrder(data)
		} catch (error) {
			console.error('Failed to fetch order:', error)
		} finally {
			setLoading(false)
		}
	}

	if (loading) return <LoadingSpinner size="lg" text="Loading order..." />

	if (!order) {
		return (
			<div className="page-container text-center py-16">
				<div className="text-6xl mb-4">😕</div>
				<h2 className="text-xl font-bold mb-2">Order not found</h2>
				<Link to="/orders" className="btn-primary">Go to My Orders</Link>
			</div>
		)
	}

	return (
		<div className="page-container max-w-3xl mx-auto">
			{/* Header */}
			<div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
				<div>
					<h1 className="text-2xl font-bold text-gray-900 break-words">{order.order_id}</h1>
					<p className="text-gray-500 text-sm">{formatDateTime(order.created_at)}</p>
				</div>
				<div className="flex items-center flex-wrap gap-2">
					<PriorityBadge priority={order.priority} />
					<StatusBadge status={order.status} />
				</div>
			</div>

			{/* Progress Bar */}
			<div className="card mb-6">
				<h2 className="font-bold text-gray-900 mb-4">Order Progress</h2>
				<ProgressBar currentStatus={order.status} />
			</div>

			{/* ETA */}
			{order.ai_predicted_eta && !['Delivered', 'Cancelled', 'Rejected'].includes(order.status) && (
				<div className="mb-6">
					<ETADisplay eta={order.ai_predicted_eta} />
				</div>
			)}

			{/* Order Details */}
			<div className="card mb-6">
				<h2 className="font-bold text-gray-900 mb-4">Order Details</h2>

				<div className="space-y-3 text-sm">
					<div className="flex justify-between gap-3">
						<span className="text-gray-500">Station</span>
						<span className="font-medium break-words text-right">{order.station_id}</span>
					</div>
					{order.runner_id && (
						<div className="flex justify-between gap-3">
							<span className="text-gray-500">Runner</span>
							<span className="font-medium break-words text-right">{order.runner_id}</span>
						</div>
					)}
					{order.special_instructions && (
						<div className="flex justify-between gap-3">
							<span className="text-gray-500">Instructions</span>
							<span className="font-medium break-words text-right">{order.special_instructions}</span>
						</div>
					)}
					<hr />
					<div className="flex justify-between gap-3 font-bold text-lg">
						<span>Total</span>
						<span className="text-primary-700 text-right">{formatPrice(order.total_price)}</span>
					</div>
				</div>
			</div>

			{/* Actions */}
			<div className="flex flex-col sm:flex-row gap-3">
				{['Placed', 'Confirmed'].includes(order.status) && (
					<button
						onClick={async () => {
							try {
								await orderApi.cancelOrder(orderId)
								fetchOrder()
							} catch (e) { /* handled */ }
						}}
						className="btn-danger w-full sm:w-auto"
					>
						Cancel Order
					</button>
				)}
				{order.status === 'Delivered' && (
					<Link to={`/feedback/${orderId}`} className="btn-primary w-full sm:w-auto text-center">
						Give Feedback
					</Link>
				)}
				<Link to="/orders" className="btn-secondary w-full sm:w-auto text-center">
					My Orders
				</Link>
			</div>

			{/* Trivia Popup */}
			{showTrivia && (
				<TriviaPopup onClose={() => setShowTrivia(false)} />
			)}
		</div>
	)
}
