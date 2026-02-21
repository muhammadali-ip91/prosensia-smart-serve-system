import { useCart } from '../../hooks/useCart'

export default function SpecialInstructions() {
	const { specialInstructions, setSpecialInstructions } = useCart()

	return (
		<div>
			<label className="input-label">Special Instructions (Optional)</label>
			<textarea
				value={specialInstructions}
				onChange={(e) => setSpecialInstructions(e.target.value)}
				placeholder="e.g., Less spicy, no onions..."
				maxLength={500}
				rows={3}
				className="input-field resize-none"
			/>
			<p className="text-xs text-gray-400 mt-1 text-right">
				{specialInstructions.length}/500
			</p>
		</div>
	)
}
