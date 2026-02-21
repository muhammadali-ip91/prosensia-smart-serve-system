import { STATUS_COLORS, STATUS_LABELS } from '../../utils/constants'

export default function Badge({ text, variant = 'default', size = 'sm' }) {
	const variants = {
		default: 'bg-gray-100 text-gray-800',
		primary: 'bg-primary-100 text-primary-800',
		success: 'bg-green-100 text-green-800',
		warning: 'bg-yellow-100 text-yellow-800',
		danger: 'bg-red-100 text-red-800',
		info: 'bg-blue-100 text-blue-800',
		urgent: 'bg-red-100 text-red-800',
		regular: 'bg-blue-100 text-blue-800',
	}

	const sizes = {
		xs: 'px-2 py-0.5 text-xs',
		sm: 'px-2.5 py-0.5 text-xs',
		md: 'px-3 py-1 text-sm',
	}

	return (
		<span className={`inline-flex items-center rounded-full font-medium ${variants[variant] || variants.default} ${sizes[size]}`}>
			{text}
		</span>
	)
}

export function StatusBadge({ status }) {
	const statusVariants = {
		Placed: 'info',
		Confirmed: 'info',
		Preparing: 'warning',
		Ready: 'success',
		PickedUp: 'primary',
		OnTheWay: 'primary',
		Delivered: 'success',
		Cancelled: 'danger',
		Rejected: 'danger',
		Delayed: 'warning',
	}

	return (
		<Badge
			text={STATUS_LABELS[status] || status}
			variant={statusVariants[status] || 'default'}
		/>
	)
}

export function PriorityBadge({ priority }) {
	return (
		<Badge
			text={priority}
			variant={priority === 'Urgent' ? 'urgent' : 'regular'}
		/>
	)
}
