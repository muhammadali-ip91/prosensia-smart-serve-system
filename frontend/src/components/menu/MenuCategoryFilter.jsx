export default function MenuCategoryFilter({ categories, selected, onSelect }) {
	return (
		<div className="flex flex-wrap gap-2 mb-6">
			<button
				onClick={() => onSelect('All')}
				className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
					selected === 'All'
						? 'bg-primary-600 text-white'
						: 'bg-gray-100 text-gray-600 hover:bg-gray-200'
				}`}
			>
				All
			</button>
			{categories.map(cat => (
				<button
					key={cat}
					onClick={() => onSelect(cat)}
					className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
						selected === cat
							? 'bg-primary-600 text-white'
							: 'bg-gray-100 text-gray-600 hover:bg-gray-200'
					}`}
				>
					{cat}
				</button>
			))}
		</div>
	)
}
