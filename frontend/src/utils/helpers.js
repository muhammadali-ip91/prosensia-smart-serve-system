// Get station ID from URL params
export function getStationFromURL() {
	const params = new URLSearchParams(window.location.search)
	return params.get('station') || ''
}

// Truncate text
export function truncate(text, maxLength = 50) {
	if (!text) return ''
	if (text.length <= maxLength) return text
	return text.substring(0, maxLength) + '...'
}

// Get initials from name
export function getInitials(name) {
	if (!name) return '?'
	return name
		.split(' ')
		.map(word => word[0])
		.join('')
		.toUpperCase()
		.substring(0, 2)
}

// Capitalize first letter
export function capitalize(str) {
	if (!str) return ''
	return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

// Check if current time is peak hour
export function isPeakHour() {
	const hour = new Date().getHours()
	return (hour >= 12 && hour < 14) || (hour >= 18 && hour < 20)
}

// Debounce function
export function debounce(func, wait) {
	let timeout
	return function executedFunction(...args) {
		const later = () => {
			clearTimeout(timeout)
			func(...args)
		}
		clearTimeout(timeout)
		timeout = setTimeout(later, wait)
	}
}
