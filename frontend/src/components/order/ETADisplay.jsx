import { formatMinutes } from '../../utils/formatters'
import { HiOutlineClock } from 'react-icons/hi'

export default function ETADisplay({ eta, confidence, source, factors }) {
	const getConfidenceColor = (conf) => {
		if (conf >= 0.8) return 'text-green-600'
		if (conf >= 0.6) return 'text-yellow-600'
		return 'text-red-600'
	}

	return (
		<div className="bg-primary-50 border border-primary-200 rounded-xl p-4">
			<div className="flex items-center space-x-3">
				<div className="bg-primary-100 p-3 rounded-full">
					<HiOutlineClock className="w-6 h-6 text-primary-600" />
				</div>
				<div>
					<p className="text-sm text-primary-600 font-medium">Estimated Delivery</p>
					<p className="text-2xl font-bold text-primary-800">
						{formatMinutes(eta)}
					</p>
				</div>
			</div>

			{confidence && (
				<div className="mt-3 flex items-center space-x-4 text-sm">
					<span className={`font-medium ${getConfidenceColor(confidence)}`}>
						Confidence: {Math.round(confidence * 100)}%
					</span>
					{source === 'fallback' && (
						<span className="text-gray-500 italic">(estimated)</span>
					)}
				</div>
			)}

			{factors && (
				<div className="mt-3 grid grid-cols-3 gap-2 text-xs">
					<div className="bg-white rounded-lg p-2 text-center">
						<p className="text-gray-500">Kitchen</p>
						<p className="font-semibold">{factors.kitchen_load}</p>
					</div>
					<div className="bg-white rounded-lg p-2 text-center">
						<p className="text-gray-500">Runners</p>
						<p className="font-semibold">{factors.runner_availability}</p>
					</div>
					<div className="bg-white rounded-lg p-2 text-center">
						<p className="text-gray-500">Complexity</p>
						<p className="font-semibold">{factors.item_complexity}</p>
					</div>
				</div>
			)}
		</div>
	)
}
