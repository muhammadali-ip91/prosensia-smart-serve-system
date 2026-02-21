import { useState } from 'react'
import { Link } from 'react-router-dom'
import { HiOutlineX, HiOutlineLightBulb } from 'react-icons/hi'

export default function TriviaPopup({ onClose }) {
	const [dismissed, setDismissed] = useState(false)

	if (dismissed) return null

	return (
		<div className="fixed bottom-6 right-6 z-40 animate-slide-in">
			<div className="bg-white rounded-2xl shadow-2xl border border-gray-200 p-6 max-w-sm">
				<div className="flex items-start justify-between mb-3">
					<div className="flex items-center space-x-2">
						<HiOutlineLightBulb className="w-6 h-6 text-yellow-500" />
						<h3 className="font-bold text-gray-900">While you wait...</h3>
					</div>
					<button
						onClick={() => { setDismissed(true); onClose() }}
						className="text-gray-400 hover:text-gray-600"
					>
						<HiOutlineX className="w-5 h-5" />
					</button>
				</div>

				<p className="text-sm text-gray-600 mb-4">
					Your order is being prepared! Play a quick trivia game while you wait? 🧠
				</p>

				<div className="flex space-x-2">
					<Link
						to="/trivia"
						className="btn-primary btn-sm flex-1 text-center"
					>
						🎮 Play Trivia
					</Link>
					<button
						onClick={() => setDismissed(true)}
						className="btn-secondary btn-sm"
					>
						No thanks
					</button>
				</div>
			</div>
		</div>
	)
}
