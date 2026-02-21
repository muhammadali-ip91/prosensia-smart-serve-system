import { Link } from 'react-router-dom'
import { StatusBadge, PriorityBadge } from '../common/Badge'
import { formatPrice, formatDateTime, formatMinutes } from '../../utils/formatters'

export default function OrderCard({ order }) {
	const isActive = !['Delivered', 'Cancelled', 'Rejected'].includes(order.status)

	return (
		<div className={`card-compact ${isActive ? 'border-l-4 border-l-primary-500' : ''}`}>
			<div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
				<div>
					<div className="flex items-center flex-wrap gap-2 mb-1">
						<h3 className="font-bold text-gray-900">{order.order_id}</h3>
						<PriorityBadge priority={order.priority} />
					</div>
					<p className="text-sm text-gray-500 break-words">
						Station: {order.station_id} • {formatDateTime(order.created_at)}
					</p>
				</div>
				<StatusBadge status={order.status} />
			</div>

			{/* Items */}
			<div className="mt-3">
				{order.items?.map(item => (
					<p key={item.order_item_id} className="text-sm text-gray-600">
						{item.quantity}x Item #{item.item_id} — {formatPrice(item.subtotal)}
					</p>
				))}
			</div>

			{/* Footer */}
			<div className="mt-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-3 border-t border-gray-100">
				<div className="text-sm">
					<span className="text-gray-500">Total: </span>
					<span className="font-bold text-gray-900">{formatPrice(order.total_price)}</span>
					{order.ai_predicted_eta && (
						<span className="text-gray-400 block sm:inline sm:ml-3 mt-1 sm:mt-0">
							ETA: {formatMinutes(order.ai_predicted_eta)}
						</span>
					)}
				</div>

				<div className="flex flex-wrap gap-2">
					{isActive && (
						<Link
							to={`/order/track/${order.order_id}`}
							className="btn-primary btn-sm"
						>
							Track
						</Link>
					)}
					{order.status === 'Delivered' && (
						<Link
							to={`/feedback/${order.order_id}`}
							className="btn-outline btn-sm"
						>
							Feedback
						</Link>
					)}
				</div>
			</div>
		</div>
	)
}
