import { useState } from 'react'
import { useCart } from '../../hooks/useCart'
import { formatPrice, formatMinutes } from '../../utils/formatters'
import QuantitySelector from './QuantitySelector'
import { HiOutlinePlus, HiOutlineClock } from 'react-icons/hi'

export default function MenuItemCard({ item }) {
	const { addToCart, cartItems } = useCart()
	const [quantity, setQuantity] = useState(1)
	const [imageError, setImageError] = useState(false)

	const inCart = cartItems.find(ci => ci.item_id === item.item_id)

	const handleAdd = () => {
		addToCart(item, quantity)
		setQuantity(1)
	}

	const defaultApiUrl = typeof window !== 'undefined'
		? `${window.location.protocol}//${window.location.hostname}:8000`
		: 'http://localhost:8000'

	const apiBase = import.meta.env.VITE_API_URL || defaultApiUrl
	const imageSrc = item.image_url
		? (item.image_url.startsWith('http') ? item.image_url : `${apiBase}${item.image_url}`)
		: null

	return (
		<div className={`card transition-all ${!item.is_available ? 'opacity-50' : 'hover:shadow-lg'}`}>
			{/* Item Image */}
			<div className="bg-gradient-to-br from-primary-100 to-primary-50 rounded-lg h-40 flex items-center justify-center mb-4 overflow-hidden">
				{imageSrc && !imageError ? (
					<img
						src={imageSrc}
						alt={item.item_name}
						className="w-full h-full object-cover"
						onError={() => setImageError(true)}
					/>
				) : (
					<span className="text-5xl">
						{item.category === 'Beverages' ? '☕' :
						 item.category === 'Snacks' ? '🍟' :
						 item.category === 'Sandwiches' ? '🥪' :
						 item.category === 'Main Course' ? '🍛' :
						 item.category === 'Desserts' ? '🍮' : '🍽️'}
					</span>
				)}
			</div>

			{/* Item Info */}
			<div className="mb-3">
				<div className="flex items-start justify-between gap-2">
					<h3 className="font-bold text-gray-900 text-base sm:text-lg leading-6 break-words">
						{item.item_name}
					</h3>
					<span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full whitespace-nowrap">
						{item.category}
					</span>
				</div>

				<div className="flex items-center space-x-3 mt-2 text-sm text-gray-500">
					<div className="flex items-center space-x-1">
						<HiOutlineClock className="w-4 h-4" />
						<span>{formatMinutes(item.prep_time_estimate)}</span>
					</div>
				</div>
			</div>

			{/* Price */}
			<p className="text-lg sm:text-xl font-bold text-primary-700 mb-4">
				{formatPrice(item.price)}
			</p>

			{/* Actions */}
			{item.is_available ? (
				<div className="flex flex-col sm:flex-row sm:items-center gap-3">
					<QuantitySelector
						quantity={quantity}
						onChange={setQuantity}
						min={1}
						max={10}
					/>
					<button
						onClick={handleAdd}
						className="btn-primary w-full sm:flex-1 flex items-center justify-center space-x-2"
					>
						<HiOutlinePlus className="w-5 h-5" />
						<span>{inCart ? 'Add More' : 'Add to Cart'}</span>
					</button>
				</div>
			) : (
				<div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
					<p className="text-red-700 font-medium text-sm">Unavailable</p>
					{item.unavailable_reason && (
						<p className="text-red-500 text-xs mt-1">{item.unavailable_reason}</p>
					)}
				</div>
			)}

			{/* In Cart Indicator */}
			{inCart && (
				<p className="text-sm text-primary-600 font-medium mt-2 text-center">
					✓ {inCart.quantity} in cart
				</p>
			)}
		</div>
	)
}
