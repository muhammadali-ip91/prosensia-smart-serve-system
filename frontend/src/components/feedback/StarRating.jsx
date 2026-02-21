import { useState } from 'react'
import { HiStar } from 'react-icons/hi'

export default function StarRating({ rating, onRate, size = 'lg', readonly = false }) {
	const [hover, setHover] = useState(0)

	const sizes = {
		sm: 'w-5 h-5',
		md: 'w-8 h-8',
		lg: 'w-10 h-10',
	}

	return (
		<div className="flex items-center space-x-1">
			{[1, 2, 3, 4, 5].map(star => (
				<button
					key={star}
					type="button"
					disabled={readonly}
					onClick={() => !readonly && onRate(star)}
					onMouseEnter={() => !readonly && setHover(star)}
					onMouseLeave={() => !readonly && setHover(0)}
					className={`transition-transform ${!readonly ? 'hover:scale-110 cursor-pointer' : 'cursor-default'}`}
				>
					<HiStar
						className={`${sizes[size]} transition-colors ${
							star <= (hover || rating)
								? 'text-yellow-400'
								: 'text-gray-300'
						}`}
					/>
				</button>
			))}
			{rating > 0 && (
				<span className="ml-2 text-sm text-gray-500 font-medium">
					{rating}/5
				</span>
			)}
		</div>
	)
}
