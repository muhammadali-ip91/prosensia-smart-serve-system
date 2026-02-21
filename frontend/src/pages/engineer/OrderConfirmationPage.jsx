import { useParams, useLocation, Link } from 'react-router-dom'
import ETADisplay from '../../components/order/ETADisplay'
import { formatPrice } from '../../utils/formatters'
import { HiCheckCircle } from 'react-icons/hi'

export default function OrderConfirmationPage() {
	const { orderId } = useParams()
	const location = useLocation()
	const orderData = location.state?.orderData

	return (
		<div className="page-container max-w-2xl mx-auto">
			<div className="text-center mb-8 animate-fade-in">
				<HiCheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
				<h1 className="text-3xl font-bold text-gray-900 mb-2">Order Placed! 🎉</h1>
				<p className="text-gray-500">Your order has been received</p>
			</div>

			<div className="card space-y-6">
				{/* Order ID */}
				<div className="text-center bg-gray-50 rounded-xl p-4">
					<p className="text-sm text-gray-500">Order ID</p>
					<p className="text-2xl font-bold text-primary-700">{orderId}</p>
				</div>

				{/* ETA */}
				{orderData?.estimated_wait_time && (
					<ETADisplay
						eta={orderData.estimated_wait_time}
						confidence={orderData.eta_confidence}
						source={orderData.eta_source}
						factors={orderData.eta_factors}
					/>
				)}

				{/* Details */}
				<div className="space-y-3">
					{orderData?.assigned_runner && (
						<div className="flex justify-between text-sm">
							<span className="text-gray-500">Assigned Runner</span>
							<span className="font-medium">{orderData.assigned_runner}</span>
						</div>
					)}
					<div className="flex justify-between text-sm">
						<span className="text-gray-500">Total</span>
						<span className="font-bold text-lg">{formatPrice(orderData?.total_price || 0)}</span>
					</div>
				</div>

				{/* Actions */}
				<div className="flex flex-col sm:flex-row gap-3 pt-4">
					<Link
						to={`/order/track/${orderId}`}
						className="btn-primary flex-1 text-center"
					>
						📍 Track Order
					</Link>
					<Link
						to="/menu"
						className="btn-secondary flex-1 text-center"
					>
						Back to Menu
					</Link>
				</div>
			</div>
		</div>
	)
}
