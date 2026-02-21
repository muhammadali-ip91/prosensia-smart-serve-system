import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useCart } from '../../hooks/useCart'
import menuApi from '../../api/menuApi'
import cacheService from '../../services/cacheService'
import MenuItemCard from '../../components/menu/MenuItemCard'
import MenuCategoryFilter from '../../components/menu/MenuCategoryFilter'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import EmptyState from '../../components/common/EmptyState'
import { SkeletonCard } from '../../components/common/SkeletonLoader'
import { HiOutlineSearch } from 'react-icons/hi'
import { isPeakHour } from '../../utils/helpers'

export default function MenuPage() {
	const [menu, setMenu] = useState(null)
	const [loading, setLoading] = useState(true)
	const [searchQuery, setSearchQuery] = useState('')
	const [selectedCategory, setSelectedCategory] = useState('All')
	const [searchParams] = useSearchParams()

	const { setStationId } = useCart()

	useEffect(() => {
		// Detect station from QR URL
		const station = searchParams.get('station')
		if (station) {
			setStationId(station)
		}

		fetchMenu()
	}, [])

	const fetchMenu = async () => {
		try {
			// Try cache first
			const cached = cacheService.get('menu')
			if (cached) {
				setMenu(cached)
				setLoading(false)
				// Still refresh in background
				menuApi.getMenu().then(data => {
					setMenu(data)
					cacheService.set('menu', data)
				})
				return
			}

			const data = await menuApi.getMenu()
			setMenu(data)
			cacheService.set('menu', data)
		} catch (error) {
			console.error('Failed to load menu:', error)
		} finally {
			setLoading(false)
		}
	}

	// Get all categories
	const categories = menu?.categories?.map(c => c.category) || []

	// Get all items (flattened)
	const allItems = menu?.categories?.flatMap(c => c.items) || []

	// Filter items
	const filteredItems = allItems.filter(item => {
		const matchesSearch = item.item_name.toLowerCase().includes(searchQuery.toLowerCase())
		const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory
		return matchesSearch && matchesCategory
	})

	const stationId = searchParams.get('station')

	if (loading) {
		return (
			<div className="page-container">
				<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
					{Array.from({ length: 8 }).map((_, i) => <SkeletonCard key={i} />)}
				</div>
			</div>
		)
	}

	return (
		<div className="page-container">
			{/* Header */}
			<div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
				<div>
					<h1 className="page-title mb-0">Menu</h1>
					{stationId && (
						<p className="text-gray-500 mt-1">
							📍 You are at <span className="font-semibold text-primary-600">{stationId}</span>
						</p>
					)}
					{isPeakHour() && (
						<p className="text-orange-600 text-sm mt-1">
							🔥 Peak hours - delivery may take longer
						</p>
					)}
				</div>
				<p className="text-gray-500 text-sm mt-2 sm:mt-0">
					{menu?.total_items || 0} items available
				</p>
			</div>

			{/* Search */}
			<div className="relative mb-4">
				<HiOutlineSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
				<input
					type="text"
					value={searchQuery}
					onChange={(e) => setSearchQuery(e.target.value)}
					placeholder="Search menu items..."
					className="input-field pl-10"
				/>
			</div>

			{/* Category Filter */}
			<MenuCategoryFilter
				categories={categories}
				selected={selectedCategory}
				onSelect={setSelectedCategory}
			/>

			{/* Items Grid */}
			{filteredItems.length === 0 ? (
				<EmptyState
					icon="🍽️"
					title="No items found"
					description="Try a different search or category"
				/>
			) : (
				<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
					{filteredItems.map(item => (
						<MenuItemCard key={item.item_id} item={item} />
					))}
				</div>
			)}
		</div>
	)
}
