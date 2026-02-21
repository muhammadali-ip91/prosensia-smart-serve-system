// Email validation
export function isValidEmail(email) {
	const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
	return re.test(email)
}

// Password validation (minimum 6 chars)
export function isValidPassword(password) {
	return password && password.length >= 6
}

// Not empty
export function isNotEmpty(value) {
	return value && value.trim().length > 0
}

// Valid rating (1-5)
export function isValidRating(rating) {
	return rating >= 1 && rating <= 5
}

// Valid quantity (1-10)
export function isValidQuantity(qty) {
	return qty >= 1 && qty <= 10
}
