import { useCart } from '../../hooks/useCart'

export default function PriorityToggle() {
	const { priority, setPriority } = useCart()

	return (
		<div>
			<label className="input-label">Priority</label>
			<div className="flex gap-2 sm:gap-3">
				<button
					onClick={() => setPriority('Regular')}
					className={`flex-1 py-2.5 sm:py-3 rounded-lg text-xs sm:text-sm font-medium border-2 transition-all whitespace-nowrap ${
						priority === 'Regular'
							? 'border-primary-600 bg-primary-50 text-primary-700'
							: 'border-gray-200 text-gray-500 hover:border-gray-300'
					}`}
				>
					🟢 Regular
				</button>
				<button
					onClick={() => setPriority('Urgent')}
					className={`flex-1 py-2.5 sm:py-3 rounded-lg text-xs sm:text-sm font-medium border-2 transition-all whitespace-nowrap ${
						priority === 'Urgent'
							? 'border-red-500 bg-red-50 text-red-700'
							: 'border-gray-200 text-gray-500 hover:border-gray-300'
					}`}
				>
					🔴 Urgent
				</button>
			</div>
		</div>
	)
}
