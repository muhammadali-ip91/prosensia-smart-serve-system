import { useCart } from '../../hooks/useCart'
import { formatPrice } from '../../utils/formatters'
import QuantitySelector from '../menu/QuantitySelector'
import { HiOutlineTrash } from 'react-icons/hi'

export default function CartItem({ item }) {
	const { updateQuantity, removeFromCart } = useCart()

	return (
		<div className="py-4 border-b border-gray-100 last:border-0">
			<div className="flex items-start gap-3">
				<div className="w-14 h-14 bg-primary-50 rounded-lg flex items-center justify-center text-2xl flex-shrink-0">
					🍽️
				</div>

				<div className="flex-1 min-w-0">
					<h4 className="font-semibold text-gray-900 text-sm sm:text-base leading-5 break-words">
						{item.item_name}
					</h4>
					<p className="text-xs sm:text-sm text-gray-500">{item.category}</p>
					<p className="text-sm font-medium text-primary-700">
						{formatPrice(item.price)} each
					</p>
				</div>

				<button
					onClick={() => removeFromCart(item.item_id)}
					className="p-2 text-gray-400 hover:text-accent-red hover:bg-red-50 rounded-lg transition-colors flex-shrink-0"
					aria-label={`Remove ${item.item_name}`}
				>
					<HiOutlineTrash className="w-5 h-5" />
				</button>
			</div>

			<div className="mt-3 flex items-center justify-between gap-3">
				<QuantitySelector
					quantity={item.quantity}
					onChange={(qty) => updateQuantity(item.item_id, qty)}
				/>
				<div className="text-right min-w-[84px]">
					<p className="font-bold text-gray-900 text-base sm:text-lg leading-5">
						{formatPrice(item.price * item.quantity)}
					</p>
				</div>
			</div>
		</div>
	)
}
