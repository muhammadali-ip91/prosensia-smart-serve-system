export function SkeletonCard() {
	return (
		<div className="card animate-pulse">
			<div className="skeleton h-40 w-full mb-4 rounded-lg"></div>
			<div className="skeleton h-4 w-3/4 mb-2"></div>
			<div className="skeleton h-4 w-1/2 mb-4"></div>
			<div className="skeleton h-8 w-1/3 rounded-lg"></div>
		</div>
	)
}

export function SkeletonList({ count = 5 }) {
	return (
		<div className="space-y-3">
			{Array.from({ length: count }).map((_, i) => (
				<div key={i} className="card-compact animate-pulse flex items-center space-x-4">
					<div className="skeleton h-12 w-12 rounded-full"></div>
					<div className="flex-1">
						<div className="skeleton h-4 w-3/4 mb-2"></div>
						<div className="skeleton h-3 w-1/2"></div>
					</div>
					<div className="skeleton h-8 w-20 rounded-lg"></div>
				</div>
			))}
		</div>
	)
}

export function SkeletonTable({ rows = 5, cols = 4 }) {
	return (
		<div className="animate-pulse">
			<div className="skeleton h-10 w-full mb-2 rounded"></div>
			{Array.from({ length: rows }).map((_, i) => (
				<div key={i} className="flex space-x-4 mb-2">
					{Array.from({ length: cols }).map((_, j) => (
						<div key={j} className="skeleton h-8 flex-1 rounded"></div>
					))}
				</div>
			))}
		</div>
	)
}
