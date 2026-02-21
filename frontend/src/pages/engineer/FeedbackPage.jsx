import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import orderApi from '../../api/orderApi'
import StarRating from '../../components/feedback/StarRating'
import toast from 'react-hot-toast'

export default function FeedbackPage() {
	const { orderId } = useParams()
	const navigate = useNavigate()
	const [rating, setRating] = useState(0)
	const [comment, setComment] = useState('')
	const [loading, setLoading] = useState(false)

	const handleSubmit = async (e) => {
		e.preventDefault()

		if (rating === 0) {
			toast.error('Please select a rating')
			return
		}

		setLoading(true)
		try {
			await orderApi.submitFeedback(orderId, rating, comment || null)
			toast.success('Feedback submitted! Thank you! 🙏')
			navigate('/orders')
		} catch (error) {
			const msg = error.response?.data?.error?.message || 'Failed to submit feedback'
			toast.error(msg)
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="page-container max-w-lg mx-auto">
			<div className="card">
				<h1 className="text-2xl font-bold text-gray-900 mb-2">Rate Your Order</h1>
				<p className="text-gray-500 mb-6">Order: {orderId}</p>

				<form onSubmit={handleSubmit} className="space-y-6">
					{/* Star Rating */}
					<div className="text-center">
						<p className="text-sm text-gray-600 mb-3">How was your experience?</p>
						<div className="flex justify-center">
							<StarRating rating={rating} onRate={setRating} size="lg" />
						</div>
					</div>

					{/* Comment */}
					<div>
						<label className="input-label">Comment (Optional)</label>
						<textarea
							value={comment}
							onChange={(e) => setComment(e.target.value)}
							placeholder="Tell us about your experience..."
							maxLength={500}
							rows={4}
							className="input-field resize-none"
						/>
					</div>

					{/* Submit */}
					<button
						type="submit"
						disabled={loading || rating === 0}
						className="btn-primary w-full btn-lg"
					>
						{loading ? 'Submitting...' : 'Submit Feedback'}
					</button>
				</form>
			</div>
		</div>
	)
}
