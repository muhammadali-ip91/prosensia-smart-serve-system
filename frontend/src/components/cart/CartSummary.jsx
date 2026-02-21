import { useCart } from '../../hooks/useCart'
import { formatPrice } from '../../utils/formatters'

export default function CartSummary() {
	const { cartItems, getCartTotal, getCartCount } = useCart()

	const total = getCartTotal()
	const count = getCartCount()

	return (
		<div className="bg-gray-50 rounded-xl p-4 space-y-3">
			<h3 className="font-bold text-gray-900 text-lg">Order Summary</h3>

			<div className="space-y-2 text-sm">
				<div className="flex justify-between text-gray-600">
					<span>Items ({count})</span>
					<span>{formatPrice(total)}</span>
				</div>
				<div className="flex justify-between text-gray-600">
					<span>Delivery</span>
					<span className="text-green-600 font-medium">Free</span>
				</div>
			</div>

			<hr className="border-gray-200" />

			<div className="flex justify-between font-bold text-lg">
				<span>Total</span>
				<span className="text-primary-700">{formatPrice(total)}</span>
			</div>
		</div>
	)
}
