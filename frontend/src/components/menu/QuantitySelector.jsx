import { HiMinus, HiPlus } from 'react-icons/hi'

export default function QuantitySelector({ quantity, onChange, min = 1, max = 10 }) {
	return (
		<div className="flex items-center border border-gray-300 rounded-lg">
			<button
				onClick={() => onChange(Math.max(min, quantity - 1))}
				disabled={quantity <= min}
				className="px-2 sm:px-3 py-2 text-gray-600 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed rounded-l-lg transition-colors"
			>
				<HiMinus className="w-4 h-4" />
			</button>
			<span className="px-2 sm:px-3 py-2 text-center min-w-[34px] sm:min-w-[40px] font-bold text-gray-900 border-x border-gray-300 text-sm sm:text-base">
				{quantity}
			</span>
			<button
				onClick={() => onChange(Math.min(max, quantity + 1))}
				disabled={quantity >= max}
				className="px-2 sm:px-3 py-2 text-gray-600 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed rounded-r-lg transition-colors"
			>
				<HiPlus className="w-4 h-4" />
			</button>
		</div>
	)
}
