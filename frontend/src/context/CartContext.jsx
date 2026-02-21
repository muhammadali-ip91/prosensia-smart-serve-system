import { createContext, useState, useCallback } from 'react'
import toast from 'react-hot-toast'

export const CartContext = createContext(null)

export function CartProvider({ children }) {
	const [cartItems, setCartItems] = useState([])
	const [priority, setPriority] = useState('Regular')
	const [specialInstructions, setSpecialInstructions] = useState('')
	const [stationId, setStationId] = useState('')

	const addToCart = useCallback((menuItem, quantity = 1) => {
		setCartItems(prev => {
			const existing = prev.find(item => item.item_id === menuItem.item_id)

			if (existing) {
				// Update quantity
				const updated = prev.map(item =>
					item.item_id === menuItem.item_id
						? { ...item, quantity: item.quantity + quantity }
						: item
				)
				toast.success(`${menuItem.item_name} quantity updated`)
				return updated
			}

			// Add new item
			toast.success(`${menuItem.item_name} added to cart`)
			return [...prev, {
				item_id: menuItem.item_id,
				item_name: menuItem.item_name,
				price: menuItem.price,
				category: menuItem.category,
				prep_time_estimate: menuItem.prep_time_estimate,
				quantity: quantity
			}]
		})
	}, [])

	const removeFromCart = useCallback((itemId) => {
		setCartItems(prev => {
			const item = prev.find(i => i.item_id === itemId)
			if (item) {
				toast.success(`${item.item_name} removed from cart`)
			}
			return prev.filter(i => i.item_id !== itemId)
		})
	}, [])

	const updateQuantity = useCallback((itemId, quantity) => {
		if (quantity <= 0) {
			removeFromCart(itemId)
			return
		}

		if (quantity > 10) {
			toast.error('Maximum 10 items per item')
			return
		}

		setCartItems(prev =>
			prev.map(item =>
				item.item_id === itemId
					? { ...item, quantity }
					: item
			)
		)
	}, [removeFromCart])

	const clearCart = useCallback(() => {
		setCartItems([])
		setPriority('Regular')
		setSpecialInstructions('')
		toast.success('Cart cleared')
	}, [])

	const getCartTotal = useCallback(() => {
		return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0)
	}, [cartItems])

	const getCartCount = useCallback(() => {
		return cartItems.reduce((count, item) => count + item.quantity, 0)
	}, [cartItems])

	const getOrderPayload = useCallback(() => {
		return {
			station_id: stationId,
			items: cartItems.map(item => ({
				item_id: item.item_id,
				quantity: item.quantity
			})),
			priority,
			special_instructions: specialInstructions || null
		}
	}, [cartItems, stationId, priority, specialInstructions])

	const value = {
		cartItems,
		priority,
		specialInstructions,
		stationId,
		addToCart,
		removeFromCart,
		updateQuantity,
		clearCart,
		setPriority,
		setSpecialInstructions,
		setStationId,
		getCartTotal,
		getCartCount,
		getOrderPayload,
		isEmpty: cartItems.length === 0,
	}

	return (
		<CartContext.Provider value={value}>
			{children}
		</CartContext.Provider>
	)
}
