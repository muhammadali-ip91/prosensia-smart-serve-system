import { STATUS_FLOW, STATUS_LABELS, STATUS_COLORS } from '../../utils/constants'
import { HiCheck } from 'react-icons/hi'

export default function ProgressBar({ currentStatus }) {
	const currentIndex = STATUS_FLOW.indexOf(currentStatus)

	// Handle cancelled/rejected
	if (currentStatus === 'Cancelled' || currentStatus === 'Rejected') {
		return (
			<div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
				<div className="text-4xl mb-2">❌</div>
				<p className="text-red-700 font-semibold text-lg">
					Order {currentStatus}
				</p>
			</div>
		)
	}

	return (
		<div className="py-4">
			<div className="sm:hidden">
				<div className="grid grid-cols-4 gap-2">
					{STATUS_FLOW.map((status, index) => {
						const isCompleted = index < currentIndex
						const isCurrent = index === currentIndex

						return (
							<div key={status} className="flex flex-col items-center text-center">
								<div
									className={`w-full rounded-xl border px-2 py-2 transition-all duration-300 ${
										isCurrent
											? 'border-blue-300 bg-blue-50/70'
											: isCompleted
											? 'border-green-300 bg-green-50/70'
											: 'border-gray-200 bg-gray-50'
									}`}
								>
									<div
										className={`mx-auto w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-500 ${
											isCompleted
												? 'bg-green-500 text-white'
												: isCurrent
												? `${STATUS_COLORS[status] || 'bg-blue-500'} text-white ring-2 ring-offset-1 ring-blue-200`
												: 'bg-gray-200 text-gray-500'
										}`}
									>
										{isCompleted ? <HiCheck className="w-4 h-4" /> : index + 1}
									</div>
									<span
										className={`block text-[11px] leading-4 mt-2 font-medium min-h-[2.2rem] ${
											isCurrent ? 'text-primary-700 font-bold' : isCompleted ? 'text-green-600' : 'text-gray-400'
										}`}
									>
										{STATUS_LABELS[status]}
									</span>
								</div>
							</div>
						)
					})}
				</div>

				<div className="mt-3 h-2 rounded-full bg-gray-200 overflow-hidden">
					<div
						className="h-full bg-blue-500 transition-all duration-500"
						style={{ width: `${Math.max(0, Math.min(100, ((currentIndex + 1) / STATUS_FLOW.length) * 100))}%` }}
					/>
				</div>
			</div>

			<div className="hidden sm:flex items-center justify-between">
				{STATUS_FLOW.map((status, index) => {
					const isCompleted = index < currentIndex
					const isCurrent = index === currentIndex
					const isPending = index > currentIndex

					return (
						<div key={status} className="flex items-center flex-1">
							{/* Step Circle */}
							<div className="flex flex-col items-center">
								<div
									className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-500 ${
										isCompleted
											? 'bg-green-500 text-white'
											: isCurrent
											? `${STATUS_COLORS[status] || 'bg-blue-500'} text-white ring-4 ring-offset-2 ring-blue-200 animate-pulse-slow`
											: 'bg-gray-200 text-gray-500'
									}`}
								>
									{isCompleted ? (
										<HiCheck className="w-5 h-5" />
									) : (
										index + 1
									)}
								</div>
								<span
									className={`text-xs mt-2 font-medium text-center max-w-[70px] ${
										isCurrent ? 'text-primary-700 font-bold' : isCompleted ? 'text-green-600' : 'text-gray-400'
									}`}
								>
									{STATUS_LABELS[status]}
								</span>
							</div>

							{/* Connector Line */}
							{index < STATUS_FLOW.length - 1 && (
								<div className="flex-1 h-1 mx-2 mt-[-20px]">
									<div
										className={`h-full rounded-full transition-all duration-500 ${
											isCompleted ? 'bg-green-500' : 'bg-gray-200'
										}`}
									></div>
								</div>
							)}
						</div>
					)
				})}
			</div>
		</div>
	)
}
