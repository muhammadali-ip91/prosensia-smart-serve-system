import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useCart } from '../../hooks/useCart'
import orderApi from '../../api/orderApi'
import CartItem from '../../components/cart/CartItem'
import CartSummary from '../../components/cart/CartSummary'
import PriorityToggle from '../../components/cart/PriorityToggle'
import SpecialInstructions from '../../components/cart/SpecialInstructions'
import EmptyState from '../../components/common/EmptyState'
import toast from 'react-hot-toast'

export default function CartPage() {
	const { cartItems, isEmpty, getOrderPayload, stationId, setStationId, clearCart } = useCart()
	const [loading, setLoading] = useState(false)
	const navigate = useNavigate()

	const handlePlaceOrder = async () => {
		if (!stationId) {
			toast.error('Please enter your station ID')
			return
		}

		if (isEmpty) {
			toast.error('Cart is empty')
			return
		}

		setLoading(true)
		try {
			const payload = getOrderPayload()
			const result = await orderApi.placeOrder(payload)

			clearCart()
			toast.success('Order placed successfully! 🎉')
			navigate(`/order/confirmation/${result.order_id}`, { state: { orderData: result } })
		} catch (error) {
			const message = error.response?.data?.error?.message || 'Failed to place order'
			toast.error(message)
		} finally {
			setLoading(false)
		}
	}

	if (isEmpty) {
		return (
			<div className="page-container">
				<EmptyState
					icon="🛒"
					title="Your cart is empty"
					description="Add items from the menu to get started"
					action={
						<Link to="/menu" className="btn-primary">Browse Menu</Link>
					}
				/>
			</div>
		)
	}

	return (
		<div className="page-container">
			<h1 className="page-title">Your Cart</h1>

			<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
				{/* Left: Cart Items */}
				<div className="lg:col-span-2">
					<div className="card">
						{cartItems.map(item => (
							<CartItem key={item.item_id} item={item} />
						))}
					</div>
				</div>

				{/* Right: Summary + Actions */}
				<div className="space-y-6">
					{/* Station ID */}
					<div className="card">
						<label className="input-label">Station ID</label>
						<input
							type="text"
							value={stationId}
							onChange={(e) => setStationId(e.target.value)}
							placeholder="e.g., Bay-12"
							className="input-field"
						/>
					</div>

					{/* Priority */}
					<div className="card">
						<PriorityToggle />
					</div>

					{/* Special Instructions */}
					<div className="card">
						<SpecialInstructions />
					</div>

					{/* Summary */}
					<div className="card">
						<CartSummary />
					</div>

					{/* Place Order */}
					<button
						onClick={handlePlaceOrder}
						disabled={loading || isEmpty}
						className="btn-primary w-full btn-lg flex items-center justify-center"
					>
						{loading ? (
							<>
								<div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
								Placing Order...
							</>
						) : (
							'🚀 Place Order'
						)}
					</button>
				</div>
			</div>
		</div>
	)
}
