import { format, formatDistanceToNow } from 'date-fns'

// Format price
export function formatPrice(price) {
	return `Rs. ${Number(price).toFixed(2)}`
}

// Format date
export function formatDate(dateString) {
	if (!dateString) return '-'
	return format(new Date(dateString), 'MMM dd, yyyy')
}

// Format date and time
export function formatDateTime(dateString) {
	if (!dateString) return '-'
	return format(new Date(dateString), 'MMM dd, yyyy hh:mm a')
}

// Format time only
export function formatTime(dateString) {
	if (!dateString) return '-'
	return format(new Date(dateString), 'hh:mm a')
}

// Time ago
export function timeAgo(dateString) {
	if (!dateString) return '-'
	return formatDistanceToNow(new Date(dateString), { addSuffix: true })
}

// Format minutes
export function formatMinutes(minutes) {
	if (!minutes && minutes !== 0) return '-'
	if (minutes < 1) return 'Less than 1 min'
	if (minutes === 1) return '1 min'
	return `${Math.round(minutes)} min`
}

// Format percentage
export function formatPercent(value) {
	if (!value && value !== 0) return '-'
	return `${Number(value).toFixed(1)}%`
}
