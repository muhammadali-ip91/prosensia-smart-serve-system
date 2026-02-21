const storageService = {
	// Get item
	get(key) {
		try {
			const item = localStorage.getItem(key)
			return item ? JSON.parse(item) : null
		} catch {
			return null
		}
	},

	// Set item
	set(key, value) {
		try {
			localStorage.setItem(key, JSON.stringify(value))
		} catch (e) {
			console.error('Storage error:', e)
		}
	},

	// Remove item
	remove(key) {
		localStorage.removeItem(key)
	},

	// Clear all
	clear() {
		localStorage.clear()
	},
}

export default storageService
